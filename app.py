import streamlit as st
import pandas as pd
import base64
import re
import json
import io
from urllib.parse import urlparse
from web_scraper import get_website_text_content
from database import ScrapingDatabase
from scheduler import get_scheduler
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import openpyxl
from openpyxl import Workbook
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

# Admin credentials from environment variables
import os
# Set admin credentials as requested
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "your_username")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "your_secure_password")

def is_valid_url(url):
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def authenticate_user(username, password):
    """Authenticate user with hardcoded credentials"""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def create_download_link(data, filename, file_type="text"):
    """Create download link for scraped data"""
    if file_type == "csv":
        if isinstance(data, list):  # Multiple URLs data
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame({"Scraped Content": [data]})
        csv_string = df.to_csv(index=False)
        b64 = base64.b64encode(csv_string.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download as CSV</a>'
    elif file_type == "json":
        if isinstance(data, list):
            json_string = json.dumps(data, indent=2)
        else:
            json_string = json.dumps({"content": data}, indent=2)
        b64 = base64.b64encode(json_string.encode()).decode()
        href = f'<a href="data:file/json;base64,{b64}" download="{filename}.json">Download as JSON</a>'
    elif file_type == "excel":
        # Create Excel file
        output = io.BytesIO()
        wb = Workbook()
        ws = wb.active
        
        if ws is not None:
            if isinstance(data, list):  # Multiple URLs data
                headers = list(data[0].keys()) if data else []
                if headers:
                    ws.append(headers)
                    for row in data:
                        ws.append([str(row.get(col, '')) for col in headers])
            else:
                ws.append(["Content"])
                ws.append([data])
            
        wb.save(output)
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">Download as Excel</a>'
    elif file_type == "pdf":
        # Create PDF file
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        if isinstance(data, list):
            for item in data:
                story.append(Paragraph(f"<b>URL:</b> {item.get('url', '')}", styles['Normal']))
                story.append(Paragraph(f"<b>Content:</b> {item.get('content', '')[:500]}...", styles['Normal']))
                story.append(Spacer(1, 12))
        else:
            story.append(Paragraph(data[:2000], styles['Normal']))
        
        doc.build(story)
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}.pdf">Download as PDF</a>'
    else:
        # Text file download
        if isinstance(data, list):
            text_content = "\n\n".join([f"URL: {item.get('url', '')}\nContent: {item.get('content', '')}" for item in data])
        else:
            text_content = data
        b64 = base64.b64encode(text_content.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="{filename}.txt">Download as Text</a>'
    return href

def login_page():
    """Display login page"""
    st.title("🔐 Web Scraper Admin Login")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Admin Authentication")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

def main_app():
    """Main application interface"""
    # Sidebar
    with st.sidebar:
        st.title("🕸️ Web Scraper")
        st.markdown(f"**Logged in as:** {st.session_state.username}")
        
        if st.button("Logout", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Navigation")
        page = st.selectbox("Select Page", ["Single URL", "Batch Scraping", "History", "Search", "Scheduled", "About"])
    
    # Main content area
    if page == "Single URL":
        scraper_page()
    elif page == "Batch Scraping":
        batch_scraper_page()
    elif page == "History":
        history_page()
    elif page == "Search":
        search_page()
    elif page == "Scheduled":
        scheduled_page()
    elif page == "About":
        about_page()

def scraper_page():
    """Main scraper interface"""
    st.title("🌐 Web Scraper Dashboard")
    st.markdown("Enter a URL below to scrape its content legally and ethically.")
    
    # URL input section
    st.subheader("🎯 Target Website")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input(
            "Website URL",
            placeholder="https://example.com",
            help="Enter a valid URL to scrape content from"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        scrape_button = st.button("🚀 Scrape", type="primary", use_container_width=True)
    
    # URL validation
    if url:
        if is_valid_url(url):
            st.success(f"✅ Valid URL: {url}")
        else:
            st.error("❌ Invalid URL format. Please enter a valid URL starting with http:// or https://")
    
    # Scraping logic
    if scrape_button and url:
        if not is_valid_url(url):
            st.error("Please enter a valid URL before scraping.")
            return
        
        # Progress indicators
        st.markdown("---")
        st.subheader("📊 Scraping Progress")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Fetching URL
            status_text.text("🔄 Fetching website content...")
            progress_bar.progress(25)
            time.sleep(0.5)  # Small delay for better UX
            
            # Step 2: Processing
            status_text.text("🔄 Processing and extracting content...")
            progress_bar.progress(50)
            
            # Actual scraping
            scraped_content = get_website_text_content(url)
            
            progress_bar.progress(75)
            status_text.text("🔄 Formatting results...")
            time.sleep(0.3)
            
            progress_bar.progress(100)
            status_text.text("✅ Scraping completed successfully!")
            
            if scraped_content:
                # Display results
                st.markdown("---")
                st.subheader("📄 Scraped Content")
                
                # Content preview
                with st.expander("Preview Content", expanded=True):
                    st.text_area(
                        "Extracted Text",
                        value=scraped_content[:1000] + "..." if len(scraped_content) > 1000 else scraped_content,
                        height=300,
                        disabled=True
                    )
                
                # Content statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Characters", len(scraped_content))
                with col2:
                    st.metric("Words", len(scraped_content.split()))
                with col3:
                    st.metric("Lines", len(scraped_content.split('\n')))
                
                # Download options
                st.markdown("---")
                st.subheader("💾 Download Options")
                
                col1, col2 = st.columns(2)
                
                # Generate filename from URL
                domain = urlparse(url).netloc.replace('www.', '')
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"{domain}_{timestamp}"
                
                with col1:
                    # Text download
                    txt_link = create_download_link(scraped_content, filename, "text")
                    st.markdown(txt_link, unsafe_allow_html=True)
                
                with col2:
                    # CSV download
                    csv_link = create_download_link(scraped_content, filename, "csv")
                    st.markdown(csv_link, unsafe_allow_html=True)
                
            else:
                st.warning("⚠️ No content could be extracted from the provided URL. The website might have protection against scraping or contain no extractable text.")
                
        except Exception as e:
            progress_bar.progress(100)
            status_text.text("❌ Scraping failed!")
            st.error(f"Error occurred while scraping: {str(e)}")
            st.info("💡 **Troubleshooting Tips:**\n"
                   "- Ensure the URL is accessible and public\n"
                   "- Check if the website allows scraping (robots.txt)\n"
                   "- Try again in a few moments\n"
                   "- Some websites may block automated requests")

def batch_scraper_page():
    """Batch scraping interface"""
    db = ScrapingDatabase()
    
    st.title("🔄 Batch Web Scraper")
    st.markdown("Scrape multiple URLs at once and save results to history.")
    
    # URL input section
    st.subheader("🎯 Target URLs")
    
    # Session name
    col1, col2 = st.columns([2, 1])
    with col1:
        session_name = st.text_input(
            "Session Name",
            value=f"Batch_{datetime.now().strftime('%Y%m%d_%H%M')}",
            help="Name for this batch scraping session"
        )
    
    # URL input methods
    url_input_method = st.radio("Choose input method:", ["Text Area", "File Upload"])
    
    urls = []
    if url_input_method == "Text Area":
        url_text = st.text_area(
            "URLs (one per line)",
            placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com",
            height=150,
            help="Enter one URL per line"
        )
        if url_text:
            urls = [url.strip() for url in url_text.split('\n') if url.strip()]
    else:
        uploaded_file = st.file_uploader("Upload a text file with URLs", type=['txt'])
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            urls = [url.strip() for url in content.split('\n') if url.strip()]
    
    # Validate URLs
    valid_urls = []
    invalid_urls = []
    
    if urls:
        st.subheader(f"📋 URL Validation ({len(urls)} URLs found)")
        
        for url in urls:
            if is_valid_url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"✅ Valid URLs: {len(valid_urls)}")
        with col2:
            if invalid_urls:
                st.error(f"❌ Invalid URLs: {len(invalid_urls)}")
                with st.expander("View invalid URLs"):
                    for invalid_url in invalid_urls:
                        st.write(f"• {invalid_url}")
    
    # Batch scraping
    if valid_urls and st.button("🚀 Start Batch Scraping", type="primary", use_container_width=True):
        if not session_name.strip():
            st.error("Please enter a session name.")
            return
        
        # Create session
        session_id = db.create_session(session_name, len(valid_urls))
        
        # Progress tracking
        st.markdown("---")
        st.subheader("📊 Batch Scraping Progress")
        
        overall_progress = st.progress(0)
        current_url_text = st.empty()
        results_container = st.container()
        
        scraped_data = []
        successful_scrapes = 0
        
        for i, url in enumerate(valid_urls):
            current_url_text.text(f"🔄 Scraping {i+1}/{len(valid_urls)}: {url}")
            
            try:
                content = get_website_text_content(url)
                if content:
                    # Extract title if possible
                    title = url.split('/')[-1] if '/' in url else url
                    
                    # Save to database
                    db.save_scraped_data(session_id, url, content, title)
                    scraped_data.append({
                        'url': url,
                        'title': title,
                        'content': content,
                        'word_count': len(content.split()),
                        'char_count': len(content),
                        'status': 'success'
                    })
                    successful_scrapes += 1
                    
                    # Show progress
                    with results_container:
                        st.success(f"✅ {url} - {len(content.split())} words")
                else:
                    db.save_scraped_data(session_id, url, "", "", "failed", "No content extracted")
                    with results_container:
                        st.warning(f"⚠️ {url} - No content extracted")
                        
            except Exception as e:
                error_msg = str(e)
                db.save_scraped_data(session_id, url, "", "", "failed", error_msg)
                with results_container:
                    st.error(f"❌ {url} - Error: {error_msg}")
            
            # Update progress
            overall_progress.progress((i + 1) / len(valid_urls))
            db.update_session_progress(session_id, i + 1)
            time.sleep(0.1)  # Small delay to prevent overwhelming
        
        # Final status
        db.update_session_progress(session_id, len(valid_urls), 'completed')
        current_url_text.text(f"✅ Completed! Successfully scraped {successful_scrapes}/{len(valid_urls)} URLs")
        
        # Results summary
        if scraped_data:
            st.markdown("---")
            st.subheader("📄 Batch Results Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total URLs", len(valid_urls))
            with col2:
                st.metric("Successful", successful_scrapes)
            with col3:
                st.metric("Failed", len(valid_urls) - successful_scrapes)
            with col4:
                total_words = sum(item['word_count'] for item in scraped_data)
                st.metric("Total Words", total_words)
            
            # Export options
            st.markdown("---")
            st.subheader("💾 Export Batch Results")
            
            filename = f"{session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                txt_link = create_download_link(scraped_data, filename, "text")
                st.markdown(txt_link, unsafe_allow_html=True)
            with col2:
                csv_link = create_download_link(scraped_data, filename, "csv")
                st.markdown(csv_link, unsafe_allow_html=True)
            with col3:
                json_link = create_download_link(scraped_data, filename, "json")
                st.markdown(json_link, unsafe_allow_html=True)
            with col4:
                excel_link = create_download_link(scraped_data, filename, "excel")
                st.markdown(excel_link, unsafe_allow_html=True)
            
            # PDF export
            pdf_link = create_download_link(scraped_data, filename, "pdf")
            st.markdown(pdf_link, unsafe_allow_html=True)

def history_page():
    """Scraping history and results management"""
    db = ScrapingDatabase()
    
    st.title("📚 Scraping History")
    st.markdown("View and manage your scraping sessions and results.")
    
    # Get all sessions
    sessions = db.get_sessions()
    
    if not sessions:
        st.info("📝 No scraping sessions found. Start by scraping some URLs!")
        return
    
    # Sessions overview
    st.subheader("🗂️ All Sessions")
    
    for session in sessions:
        with st.expander(f"📁 {session['session_name']} - {session['created_at']}", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**Status:** {session['status']}")
                st.write(f"**Total URLs:** {session['total_urls']}")
            with col2:
                st.write(f"**Completed:** {session['completed_urls']}")
                progress = session['completed_urls'] / max(session['total_urls'], 1)
                st.progress(progress)
            with col3:
                if st.button(f"View Details", key=f"view_{session['id']}"):
                    st.session_state.selected_session = session['id']
            with col4:
                if st.button(f"🗑️ Delete", key=f"delete_{session['id']}", type="secondary"):
                    if st.session_state.get(f"confirm_delete_{session['id']}", False):
                        db.delete_session(session['id'])
                        st.success("Session deleted!")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{session['id']}"] = True
                        st.warning("Click again to confirm deletion")
    
    # Session details
    if hasattr(st.session_state, 'selected_session') and st.session_state.selected_session:
        st.markdown("---")
        st.subheader("📄 Session Details")
        
        session_data = db.get_session_data(st.session_state.selected_session)
        
        if session_data:
            # Export session data
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Showing {len(session_data)} scraped items**")
            with col2:
                selected_session_name = next(s['session_name'] for s in sessions if s['id'] == st.session_state.selected_session)
                filename = f"{selected_session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                export_format = st.selectbox("Export as:", ["CSV", "JSON", "Excel", "PDF", "Text"])
                if st.button("Download", type="primary"):
                    export_data = []
                    for item in session_data:
                        export_data.append({
                            'url': item['url'],
                            'title': item['title'],
                            'content': item['content'],
                            'word_count': item['word_count'],
                            'char_count': item['char_count'],
                            'scraped_at': item['scraped_at'],
                            'status': item['status']
                        })
                    
                    download_link = create_download_link(export_data, filename, export_format.lower())
                    st.markdown(download_link, unsafe_allow_html=True)
            
            # Display items
            for item in session_data:
                with st.container():
                    if item['status'] == 'success':
                        st.success(f"✅ **{item['url']}**")
                        if item['title']:
                            st.write(f"**Title:** {item['title']}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Words", item['word_count'])
                        with col2:
                            st.metric("Characters", item['char_count'])
                        with col3:
                            st.write(f"**Scraped:** {item['scraped_at']}")
                        
                        # Content preview
                        if item['content']:
                            with st.expander("View Content"):
                                st.text_area(
                                    "Content",
                                    value=item['content'][:1000] + "..." if len(item['content']) > 1000 else item['content'],
                                    height=200,
                                    disabled=True,
                                    key=f"content_{item['id']}"
                                )
                    else:
                        st.error(f"❌ **{item['url']}** - Failed")
                        if item['error_message']:
                            st.write(f"**Error:** {item['error_message']}")
                    
                    st.markdown("---")

def search_page():
    """Search within scraped content"""
    db = ScrapingDatabase()
    
    st.title("🔍 Search Scraped Content")
    st.markdown("Search through all your scraped content across sessions.")
    
    # Search form
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input(
            "Search Term",
            placeholder="Enter keywords to search...",
            help="Search within titles, content, and URLs"
        )
    
    with col2:
        sessions = db.get_sessions()
        session_options = ["All Sessions"] + [f"{s['session_name']} ({s['id']})" for s in sessions]
        selected_session = st.selectbox("Filter by Session", session_options)
    
    if search_term and st.button("🔍 Search", type="primary"):
        # Get session ID if specific session selected
        session_id = None
        if selected_session != "All Sessions":
            session_id = int(selected_session.split("(")[-1].strip(")"))
        
        # Perform search
        results = db.search_content(search_term, session_id)
        
        if results:
            st.subheader(f"🎯 Search Results ({len(results)} found)")
            
            for result in results:
                with st.container():
                    st.success(f"✅ **{result['url']}**")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if result['title']:
                            st.write(f"**Title:** {result['title']}")
                        st.write(f"**Session:** {result['session_name']}")
                    with col2:
                        st.metric("Words", result['word_count'])
                        st.write(f"**Date:** {result['scraped_at']}")
                    
                    # Highlight search term in content preview
                    content_preview = result['content'][:500]
                    if search_term.lower() in content_preview.lower():
                        # Simple highlight (case insensitive)
                        highlighted = content_preview.replace(
                            search_term, 
                            f"**{search_term}**"
                        )
                        st.markdown(f"**Preview:** {highlighted}...")
                    else:
                        st.write(f"**Preview:** {content_preview}...")
                    
                    with st.expander("View Full Content"):
                        st.text_area(
                            "Full Content",
                            value=result['content'],
                            height=300,
                            disabled=True,
                            key=f"search_content_{result['id']}"
                        )
                    
                    st.markdown("---")
        else:
            st.info(f"🔍 No results found for '{search_term}'")

def scheduled_page():
    """Scheduled scraping management"""
    st.title("⏰ Scheduled Scraping")
    st.markdown("Set up automated scraping tasks with optional email notifications.")
    
    # Info box about scheduled scraping limitations
    st.info("📧 **Email Notifications**: This demo shows the interface for scheduled scraping. In a production environment, you would need to set up email service (SMTP) and a background task scheduler.")
    
    # Create new scheduled task
    with st.expander("➕ Create New Scheduled Task", expanded=True):
        st.subheader("📝 Task Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            task_name = st.text_input(
                "Task Name",
                placeholder="Daily News Scraping",
                help="Give your scheduled task a descriptive name"
            )
            
            schedule_type = st.selectbox(
                "Schedule Type",
                ["Daily", "Weekly", "Monthly", "Custom Interval"],
                help="How often should this task run?"
            )
            
        with col2:
            if schedule_type == "Daily":
                schedule_time = st.time_input("Run Time")
                schedule_value = f"daily_{schedule_time.strftime('%H:%M')}"
            elif schedule_type == "Weekly":
                day_of_week = st.selectbox("Day of Week", 
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                schedule_time = st.time_input("Run Time")
                schedule_value = f"weekly_{day_of_week}_{schedule_time.strftime('%H:%M')}"
            elif schedule_type == "Monthly":
                day_of_month = st.number_input("Day of Month", min_value=1, max_value=28, value=1)
                schedule_time = st.time_input("Run Time")
                schedule_value = f"monthly_{day_of_month}_{schedule_time.strftime('%H:%M')}"
            else:
                interval_hours = st.number_input("Interval (hours)", min_value=1, max_value=168, value=24)
                schedule_value = f"interval_{interval_hours}h"
        
        # URLs for scheduled task
        st.subheader("🎯 URLs to Scrape")
        scheduled_urls = st.text_area(
            "URLs (one per line)",
            placeholder="https://example1.com\nhttps://example2.com",
            height=100,
            help="Enter URLs to scrape on schedule"
        )
        
        # Email notifications
        st.subheader("📧 Email Notifications")
        email_notifications = st.checkbox("Send email notifications when complete")
        email_address = ""
        if email_notifications:
            email_address = st.text_input(
                "Email Address",
                placeholder="your-email@example.com",
                help="Where to send notification emails"
            )
        
        # Create task button
        if st.button("✅ Create Scheduled Task", type="primary"):
            if not task_name.strip():
                st.error("Please enter a task name.")
            elif not scheduled_urls.strip():
                st.error("Please enter at least one URL.")
            elif email_notifications and not email_address.strip():
                st.error("Please enter an email address for notifications.")
            else:
                # Validate URLs
                urls = [url.strip() for url in scheduled_urls.split('\n') if url.strip()]
                valid_urls = [url for url in urls if is_valid_url(url)]
                
                if len(valid_urls) != len(urls):
                    st.error(f"Some URLs are invalid. Please check your URLs.")
                else:
                    # Create actual scheduled task
                    try:
                        scheduler = get_scheduler()
                        task_id = scheduler.create_scheduled_task(
                            task_name, valid_urls, schedule_type, schedule_value,
                            email_notifications, email_address
                        )
                        
                        st.success(f"✅ Scheduled task '{task_name}' created successfully!")
                        st.info("📋 **Task Details:**\n"
                               f"- **Name**: {task_name}\n"
                               f"- **Schedule**: {schedule_type} ({schedule_value})\n"
                               f"- **URLs**: {len(valid_urls)} URLs\n"
                               f"- **Email**: {'Yes' if email_notifications else 'No'}")
                        
                        if email_notifications:
                            st.write(f"- **Email Address**: {email_address}")
                        
                        st.info("📧 **Email Setup**: To receive email notifications, set the following environment variables:\n"
                               "- SMTP_SERVER (default: smtp.gmail.com)\n"
                               "- SMTP_PORT (default: 587)\n"
                               "- SMTP_USERNAME\n"
                               "- SMTP_PASSWORD")
                               
                    except Exception as e:
                        st.error(f"❌ Failed to create scheduled task: {str(e)}")
                        st.info("💡 The scheduler is running in demo mode. In production, ensure the background scheduler service is properly configured.")
    
    # Real scheduled tasks display
    st.markdown("---")
    st.subheader("📅 Active Scheduled Tasks")
    
    # Get real scheduled tasks from database
    db = ScrapingDatabase()
    scheduled_tasks = db.get_scheduled_tasks()
    
    if not scheduled_tasks:
        st.info("📝 No scheduled tasks found. Create one above to get started!")
    else:
        for task in scheduled_tasks:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(f"**📋 {task['task_name']}**")
                    st.write(f"🕐 {task['schedule_type']} - {task['schedule_value']}")
                    st.write(f"🌐 {len(task['urls'])} URLs")
                
                with col2:
                    status_color = "🟢" if task['is_active'] else "🔴"
                    status_text = "Active" if task['is_active'] else "Paused"
                    st.write(f"**Status:** {status_color} {status_text}")
                    if task['email_notifications'] and task['email_address']:
                        st.write(f"📧 {task['email_address']}")
                
                with col3:
                    st.write(f"**Last Run:**")
                    st.write(f"{task['last_run'] or 'Never'}")
                    st.write(f"**Created:**")
                    st.write(f"{task['created_at']}")
                
                with col4:
                    if task['is_active']:
                        if st.button(f"⏸️ Pause", key=f"pause_{task['id']}", type="secondary"):
                            try:
                                scheduler = get_scheduler()
                                scheduler.pause_task(task['id'])
                                st.success(f"Task '{task['task_name']}' paused.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to pause task: {str(e)}")
                    else:
                        if st.button(f"▶️ Resume", key=f"resume_{task['id']}", type="secondary"):
                            try:
                                scheduler = get_scheduler()
                                scheduler.resume_task(task['id'])
                                st.success(f"Task '{task['task_name']}' resumed.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to resume task: {str(e)}")
                    
                    if st.button(f"🗑️ Delete", key=f"del_sched_{task['id']}", type="secondary"):
                        if st.session_state.get(f"confirm_delete_sched_{task['id']}", False):
                            try:
                                scheduler = get_scheduler()
                                scheduler.delete_task(task['id'])
                                st.success(f"Task '{task['task_name']}' deleted.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete task: {str(e)}")
                        else:
                            st.session_state[f"confirm_delete_sched_{task['id']}"] = True
                            st.warning("Click again to confirm deletion")
                
                st.markdown("---")
    
    # Instructions for production setup
    with st.expander("🔧 Production Setup Instructions", expanded=False):
        st.markdown("""
        ### Setting Up Scheduled Scraping in Production
        
        To implement scheduled scraping with email notifications, you would need:
        
        #### 1. **Task Scheduler**
        ```python
        from apscheduler.schedulers.background import BackgroundScheduler
        import smtplib
        from email.mime.text import MIMEText
        
        scheduler = BackgroundScheduler()
        scheduler.start()
        
        def scheduled_scrape_job(task_id):
            # Load task from database
            # Perform scraping
            # Send email notification if configured
            pass
        
        # Add job to scheduler
        scheduler.add_job(scheduled_scrape_job, 'cron', 
                         hour=9, minute=0, args=[task_id])
        ```
        
        #### 2. **Email Service**
        ```python
        def send_notification(email, subject, body):
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = 'scraper@yourapp.com'
            msg['To'] = email
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login('your_email', 'your_password')
                server.send_message(msg)
        ```
        
        #### 3. **Database Schema**
        The `scheduled_tasks` table is already created in the database schema.
        
        #### 4. **Background Processing**
        Consider using Celery with Redis/RabbitMQ for robust task processing.
        """)

def about_page():
    """About page with application information"""
    st.title("ℹ️ About Web Scraper")
    
    st.markdown("""
    ## 🎯 Purpose
    This web scraper application is designed to legally and ethically extract text content from websites 
    for research, analysis, and data collection purposes.
    
    ## ✨ Features
    - **Secure Access**: Admin authentication for controlled usage
    - **Legal Scraping**: Uses Trafilatura for clean, ethical content extraction
    - **Real-time Progress**: Live status updates during scraping operations
    - **Multiple Export Formats**: Download scraped data as text or CSV files
    - **Responsive Design**: Clean, mobile-friendly interface
    - **Error Handling**: Comprehensive error detection and user guidance
    
    ## 🛠️ Technology Stack
    - **Frontend**: Streamlit (Python)
    - **Scraping Engine**: Trafilatura
    - **Data Processing**: Pandas
    - **Authentication**: Session-based with hardcoded credentials
    
    ## ⚖️ Legal Notice
    This tool is intended for legal web scraping only. Please ensure you:
    - Respect website terms of service
    - Check robots.txt files
    - Don't overload servers with requests
    - Use scraped data responsibly
    
    ## 🔧 How to Use
    1. **Login**: Use admin credentials to access the application
    2. **Enter URL**: Provide a valid website URL in the scraper page
    3. **Scrape**: Click the scrape button to extract content
    4. **Download**: Save the results as text or CSV files
    
    ## 📞 Support
    For technical support or questions about this application, contact your system administrator.
    """)

def main():
    """Main application entry point"""
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # Page configuration
    st.set_page_config(
        page_title="Web Scraper Admin",
        page_icon="🕸️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling (minimal)
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Route to appropriate page based on authentication
    if st.session_state.authenticated:
        main_app()
    else:
        login_page()

if __name__ == "__main__":
    main()
