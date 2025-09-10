import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import logging

from database import ScrapingDatabase
from web_scraper import get_website_text_content

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScrapingScheduler:
    """Background scheduler for automated web scraping tasks"""
    
    def __init__(self):
        self.db = ScrapingDatabase()
        
        # Configure job store and executor
        jobstores = {
            'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
        }
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        self.scheduler.start()
        logger.info("Scheduler started successfully")
    
    def create_scheduled_task(self, task_name, urls, schedule_type, schedule_value, 
                            email_notifications=False, email_address=None):
        """Create a new scheduled scraping task"""
        try:
            # Save task to database
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scheduled_tasks 
                (task_name, urls, schedule_type, schedule_value, email_notifications, email_address, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (task_name, '\n'.join(urls), schedule_type, schedule_value, 
                  email_notifications, email_address, True))
            
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Schedule the job
            self._schedule_job(task_id, schedule_type, schedule_value)
            
            logger.info(f"Created scheduled task '{task_name}' with ID {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating scheduled task: {e}")
            raise
    
    def _schedule_job(self, task_id, schedule_type, schedule_value):
        """Schedule a job with APScheduler"""
        try:
            if schedule_type == "Daily":
                hour, minute = schedule_value.split('_')[1].split(':')
                self.scheduler.add_job(
                    self._execute_scraping_task,
                    'cron',
                    hour=int(hour),
                    minute=int(minute),
                    args=[task_id],
                    id=f'task_{task_id}',
                    replace_existing=True
                )
            
            elif schedule_type == "Weekly":
                parts = schedule_value.split('_')
                day_of_week = parts[1].lower()[:3]  # mon, tue, etc.
                hour, minute = parts[2].split(':')
                
                day_mapping = {
                    'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 
                    'fri': 4, 'sat': 5, 'sun': 6
                }
                
                self.scheduler.add_job(
                    self._execute_scraping_task,
                    'cron',
                    day_of_week=day_mapping[day_of_week],
                    hour=int(hour),
                    minute=int(minute),
                    args=[task_id],
                    id=f'task_{task_id}',
                    replace_existing=True
                )
            
            elif schedule_type == "Monthly":
                parts = schedule_value.split('_')
                day = int(parts[1])
                hour, minute = parts[2].split(':')
                
                self.scheduler.add_job(
                    self._execute_scraping_task,
                    'cron',
                    day=day,
                    hour=int(hour),
                    minute=int(minute),
                    args=[task_id],
                    id=f'task_{task_id}',
                    replace_existing=True
                )
            
            elif schedule_type == "Custom Interval":
                hours = int(schedule_value.split('_')[1].replace('h', ''))
                
                self.scheduler.add_job(
                    self._execute_scraping_task,
                    'interval',
                    hours=hours,
                    args=[task_id],
                    id=f'task_{task_id}',
                    replace_existing=True
                )
                
        except Exception as e:
            logger.error(f"Error scheduling job for task {task_id}: {e}")
            raise
    
    def _execute_scraping_task(self, task_id):
        """Execute a scheduled scraping task"""
        logger.info(f"Executing scheduled task {task_id}")
        
        try:
            # Get task details
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT task_name, urls, email_notifications, email_address
                FROM scheduled_tasks 
                WHERE id = ? AND is_active = 1
            ''', (task_id,))
            
            result = cursor.fetchone()
            if not result:
                logger.warning(f"Task {task_id} not found or inactive")
                return
            
            task_name, urls_string, email_notifications, email_address = result
            urls = [url.strip() for url in urls_string.split('\n') if url.strip()]
            
            # Update last run time
            cursor.execute('''
                UPDATE scheduled_tasks 
                SET last_run = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (task_id,))
            conn.commit()
            conn.close()
            
            # Create scraping session
            session_name = f"Scheduled_{task_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            session_id = self.db.create_session(session_name, len(urls))
            
            # Perform scraping
            successful_scrapes = 0
            failed_scrapes = 0
            scraped_data = []
            
            for url in urls:
                try:
                    content = get_website_text_content(url)
                    if content:
                        title = url.split('/')[-1] if '/' in url else url
                        self.db.save_scraped_data(session_id, url, content, title)
                        successful_scrapes += 1
                        scraped_data.append({
                            'url': url,
                            'title': title,
                            'content': content[:200] + "..." if len(content) > 200 else content,
                            'word_count': len(content.split())
                        })
                    else:
                        self.db.save_scraped_data(session_id, url, "", "", "failed", "No content extracted")
                        failed_scrapes += 1
                        
                except Exception as e:
                    error_msg = str(e)
                    self.db.save_scraped_data(session_id, url, "", "", "failed", error_msg)
                    failed_scrapes += 1
                    logger.error(f"Error scraping {url}: {error_msg}")
            
            # Update session status
            self.db.update_session_progress(session_id, len(urls), 'completed')
            
            # Send email notification if configured
            if email_notifications and email_address:
                self._send_email_notification(
                    email_address, task_name, successful_scrapes, 
                    failed_scrapes, scraped_data
                )
            
            logger.info(f"Completed scheduled task {task_id}: {successful_scrapes} successful, {failed_scrapes} failed")
            
        except Exception as e:
            logger.error(f"Error executing scheduled task {task_id}: {e}")
    
    def _send_email_notification(self, email_address, task_name, 
                               successful_scrapes, failed_scrapes, scraped_data):
        """Send email notification about scraping results"""
        try:
            # Email configuration from environment
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME', '')
            smtp_password = os.getenv('SMTP_PASSWORD', '')
            
            if not all([smtp_username, smtp_password]):
                logger.warning("SMTP credentials not configured, skipping email notification")
                return
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = email_address
            msg['Subject'] = f"Scraping Results - {task_name}"
            
            # Email body
            body = f"""
            <html>
            <body>
            <h2>Web Scraping Results</h2>
            <p><strong>Task:</strong> {task_name}</p>
            <p><strong>Completion Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>Summary</h3>
            <ul>
                <li>Successful: {successful_scrapes}</li>
                <li>Failed: {failed_scrapes}</li>
                <li>Total: {successful_scrapes + failed_scrapes}</li>
            </ul>
            
            <h3>Scraped Content Preview</h3>
            """
            
            for item in scraped_data[:5]:  # Show first 5 items
                body += f"""
                <div style="margin-bottom: 15px; border-left: 3px solid #007bff; padding-left: 10px;">
                    <strong>URL:</strong> {item['url']}<br>
                    <strong>Words:</strong> {item['word_count']}<br>
                    <strong>Preview:</strong> {item['content']}<br>
                </div>
                """
            
            if len(scraped_data) > 5:
                body += f"<p><em>... and {len(scraped_data) - 5} more items</em></p>"
            
            body += """
            <p>You can view the full results in the web scraper application's History section.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent to {email_address}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def pause_task(self, task_id):
        """Pause a scheduled task"""
        try:
            # Update database
            conn = self.db._get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE scheduled_tasks SET is_active = 0 WHERE id = ?', (task_id,))
            conn.commit()
            conn.close()
            
            # Remove from scheduler
            self.scheduler.remove_job(f'task_{task_id}')
            logger.info(f"Paused task {task_id}")
            
        except Exception as e:
            logger.error(f"Error pausing task {task_id}: {e}")
    
    def resume_task(self, task_id):
        """Resume a paused scheduled task"""
        try:
            # Get task details and re-schedule
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT schedule_type, schedule_value
                FROM scheduled_tasks 
                WHERE id = ?
            ''', (task_id,))
            
            result = cursor.fetchone()
            if result:
                schedule_type, schedule_value = result
                
                # Update database
                cursor.execute('UPDATE scheduled_tasks SET is_active = 1 WHERE id = ?', (task_id,))
                conn.commit()
                
                # Re-schedule job
                self._schedule_job(task_id, schedule_type, schedule_value)
                logger.info(f"Resumed task {task_id}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error resuming task {task_id}: {e}")
    
    def delete_task(self, task_id):
        """Delete a scheduled task"""
        try:
            # Remove from scheduler
            try:
                self.scheduler.remove_job(f'task_{task_id}')
            except JobLookupError:
                pass  # Job might not exist
            
            # Remove from database
            conn = self.db._get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM scheduled_tasks WHERE id = ?', (task_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted task {task_id}")
            
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")

# Global scheduler instance
_scheduler_instance = None

def get_scheduler():
    """Get or create scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = WebScrapingScheduler()
    return _scheduler_instance