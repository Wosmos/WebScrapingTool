import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Optional
import json

class ScrapingDatabase:
    """Database handler for scraping history and results using PostgreSQL"""
    
    def __init__(self):
        # PostgreSQL connection string
        self.db_url = os.environ.get(
            'DATABASE_URL',
            'postgresql://neondb_owner:npg_U7FlNMqc1Pjt@ep-wandering-water-addrnuvi-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
        )
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create scraping_sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_sessions (
                id SERIAL PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT DEFAULT 'pending',
                total_urls INTEGER DEFAULT 0,
                completed_urls INTEGER DEFAULT 0
            )
        ''')
        
        # Create scraped_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_data (
                id SERIAL PRIMARY KEY,
                session_id INTEGER REFERENCES scraping_sessions(id) ON DELETE CASCADE,
                url TEXT NOT NULL,
                title TEXT,
                content TEXT,
                word_count INTEGER,
                char_count INTEGER,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'success',
                error_message TEXT
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_id ON scraped_data(session_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_scraped_at ON scraped_data(scraped_at DESC)
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_name: str, total_urls: int) -> int:
        """Create a new scraping session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scraping_sessions (name, total_urls, status)
            VALUES (%s, %s, 'in_progress')
            RETURNING id
        ''', (session_name, total_urls))
        
        session_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return session_id
    
    def complete_session(self, session_id: int):
        """Mark session as completed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scraping_sessions 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (session_id,))
        
        conn.commit()
        conn.close()
    
    def save_scraped_data(self, session_id: int, url: str, content: str, 
                         title: str = "", status: str = "success", error_message: str = ""):
        """Save scraped data to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        word_count = len(content.split()) if content else 0
        char_count = len(content) if content else 0
        
        cursor.execute('''
            INSERT INTO scraped_data 
            (session_id, url, title, content, word_count, char_count, status, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (session_id, url, title, content, word_count, char_count, status, error_message))
        
        # Update completed count
        cursor.execute('''
            UPDATE scraping_sessions 
            SET completed_urls = completed_urls + 1
            WHERE id = %s
        ''', (session_id,))
        
        conn.commit()
        conn.close()
    
    def get_sessions(self) -> List[Dict]:
        """Get all scraping sessions"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT id, name, created_at, completed_at, status, total_urls, completed_urls
            FROM scraping_sessions 
            ORDER BY created_at DESC
        ''')
        
        sessions = cursor.fetchall()
        conn.close()
        return [dict(row) for row in sessions]
    
    def get_session_data(self, session_id: int) -> Dict:
        """Get session details with all scraped data"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get session info
        cursor.execute('''
            SELECT id, name, created_at, completed_at, status, total_urls, completed_urls
            FROM scraping_sessions 
            WHERE id = %s
        ''', (session_id,))
        
        session = cursor.fetchone()
        if not session:
            conn.close()
            return None
        
        # Get scraped data
        cursor.execute('''
            SELECT id, url, title, content, word_count, char_count, scraped_at, status, error_message
            FROM scraped_data 
            WHERE session_id = %s
            ORDER BY scraped_at DESC
        ''', (session_id,))
        
        data = cursor.fetchall()
        conn.close()
        
        return {
            'session': dict(session),
            'data': [dict(row) for row in data]
        }
    
    def delete_session(self, session_id: int):
        """Delete a session and all its data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM scraping_sessions WHERE id = %s', (session_id,))
        
        conn.commit()
        conn.close()
