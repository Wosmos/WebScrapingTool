import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json
import streamlit as st

class ScrapingDatabase:
    """Database handler for scraping history and results"""
    
    def __init__(self):
        # Use SQLite for simplicity in this implementation
        self.db_path = "scraping_history.db"
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create scraping_sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                total_urls INTEGER DEFAULT 0,
                completed_urls INTEGER DEFAULT 0
            )
        ''')
        
        # Create scraped_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                url TEXT NOT NULL,
                title TEXT,
                content TEXT,
                word_count INTEGER,
                char_count INTEGER,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'success',
                error_message TEXT,
                FOREIGN KEY (session_id) REFERENCES scraping_sessions (id)
            )
        ''')
        
        # Create scheduled_tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                urls TEXT NOT NULL,
                schedule_type TEXT NOT NULL,
                schedule_value TEXT,
                email_notifications BOOLEAN DEFAULT FALSE,
                email_address TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_run TIMESTAMP,
                next_run TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_name: str, total_urls: int) -> int:
        """Create a new scraping session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scraping_sessions (session_name, total_urls)
            VALUES (?, ?)
        ''', (session_name, total_urls))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id if session_id is not None else 0
    
    def update_session_progress(self, session_id: int, completed_urls: int, status: str = 'in_progress'):
        """Update session progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scraping_sessions 
            SET completed_urls = ?, status = ?
            WHERE id = ?
        ''', (completed_urls, status, session_id))
        
        conn.commit()
        conn.close()
    
    def save_scraped_data(self, session_id: int, url: str, content: str, 
                         title: str = "", status: str = "success", error_message: str = ""):
        """Save scraped data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        word_count = len(content.split()) if content else 0
        char_count = len(content) if content else 0
        
        cursor.execute('''
            INSERT INTO scraped_data 
            (session_id, url, title, content, word_count, char_count, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, url, title, content, word_count, char_count, status, error_message))
        
        conn.commit()
        conn.close()
    
    def get_sessions(self) -> List[Dict]:
        """Get all scraping sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, session_name, created_at, status, total_urls, completed_urls
            FROM scraping_sessions 
            ORDER BY created_at DESC
        ''')
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'id': row[0],
                'session_name': row[1],
                'created_at': row[2],
                'status': row[3],
                'total_urls': row[4],
                'completed_urls': row[5]
            })
        
        conn.close()
        return sessions
    
    def get_session_data(self, session_id: int) -> List[Dict]:
        """Get all scraped data for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, url, title, content, word_count, char_count, scraped_at, status, error_message
            FROM scraped_data 
            WHERE session_id = ?
            ORDER BY scraped_at DESC
        ''', (session_id,))
        
        data = []
        for row in cursor.fetchall():
            data.append({
                'id': row[0],
                'url': row[1],
                'title': row[2],
                'content': row[3],
                'word_count': row[4],
                'char_count': row[5],
                'scraped_at': row[6],
                'status': row[7],
                'error_message': row[8]
            })
        
        conn.close()
        return data
    
    def search_content(self, search_term: str, session_id: Optional[int] = None) -> List[Dict]:
        """Search within scraped content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute('''
                SELECT sd.id, sd.url, sd.title, sd.content, sd.word_count, sd.char_count, 
                       sd.scraped_at, ss.session_name
                FROM scraped_data sd
                JOIN scraping_sessions ss ON sd.session_id = ss.id
                WHERE sd.session_id = ? AND (
                    sd.content LIKE ? OR sd.title LIKE ? OR sd.url LIKE ?
                )
                ORDER BY sd.scraped_at DESC
            ''', (session_id, f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        else:
            cursor.execute('''
                SELECT sd.id, sd.url, sd.title, sd.content, sd.word_count, sd.char_count, 
                       sd.scraped_at, ss.session_name
                FROM scraped_data sd
                JOIN scraping_sessions ss ON sd.session_id = ss.id
                WHERE sd.content LIKE ? OR sd.title LIKE ? OR sd.url LIKE ?
                ORDER BY sd.scraped_at DESC
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'url': row[1],
                'title': row[2],
                'content': row[3],
                'word_count': row[4],
                'char_count': row[5],
                'scraped_at': row[6],
                'session_name': row[7]
            })
        
        conn.close()
        return results
    
    def delete_session(self, session_id: int):
        """Delete a session and all its data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM scraped_data WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM scraping_sessions WHERE id = ?', (session_id,))
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Get database connection (helper method for scheduler)"""
        return sqlite3.connect(self.db_path)
    
    def get_scheduled_tasks(self):
        """Get all scheduled tasks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, task_name, urls, schedule_type, schedule_value, 
                   email_notifications, email_address, is_active, 
                   created_at, last_run, next_run
            FROM scheduled_tasks 
            ORDER BY created_at DESC
        ''')
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'task_name': row[1],
                'urls': row[2].split('\n') if row[2] else [],
                'schedule_type': row[3],
                'schedule_value': row[4],
                'email_notifications': bool(row[5]),
                'email_address': row[6],
                'is_active': bool(row[7]),
                'created_at': row[8],
                'last_run': row[9],
                'next_run': row[10]
            })
        
        conn.close()
        return tasks