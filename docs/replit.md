# Web Scraping Application

## Overview

This is a Streamlit-based web scraping application that allows users to extract text content from websites with both manual and scheduled scraping capabilities. The application provides a user-friendly interface for managing scraping sessions, viewing historical data, and downloading results in multiple formats (CSV, PDF, Excel). It features authentication-based access control and automated background scheduling for recurring scraping tasks.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web interface
- **Design Pattern**: Single-page application with session-based state management
- **Authentication**: Environment variable-based admin credentials with session state tracking
- **User Interface**: Multi-tab layout for different functionalities (scraping, history, scheduling)

### Backend Architecture
- **Core Logic**: Python-based modular architecture with separate concerns
- **Web Scraping Engine**: Trafilatura library for robust content extraction from web pages
- **Background Processing**: APScheduler with SQLAlchemy job store for automated recurring tasks
- **Data Processing**: Pandas for data manipulation and export functionality

### Data Storage Solutions
- **Primary Database**: SQLite for simplicity and portability
- **Schema Design**: Three main tables:
  - `scraping_sessions`: Track scraping operations and their status
  - `scraped_data`: Store extracted content with metadata (word count, character count, timestamps)
  - `scheduled_tasks`: Manage recurring scraping jobs
- **File Exports**: Support for CSV, PDF (ReportLab), and Excel (openpyxl) formats

### Authentication and Authorization
- **Security Model**: Environment variable-based credentials (ADMIN_USERNAME, ADMIN_PASSWORD)
- **Session Management**: Streamlit session state for maintaining authentication status
- **Access Control**: Single admin user model with full application access

### Scheduling System
- **Scheduler**: APScheduler with background execution
- **Job Persistence**: SQLite-based job store for reliability across application restarts
- **Task Types**: Support for one-time and recurring scraping operations
- **Execution**: Thread pool executor for concurrent job processing

## External Dependencies

### Core Libraries
- **trafilatura**: Main content extraction engine for web scraping
- **streamlit**: Web application framework for user interface
- **pandas**: Data manipulation and analysis
- **sqlite3**: Built-in database connectivity
- **apscheduler**: Background job scheduling and execution

### Document Generation
- **reportlab**: PDF generation capabilities
- **openpyxl**: Excel file creation and manipulation

### Communication Services
- **smtplib**: Email notification system for scheduled task results
- **email.mime**: Email composition and formatting

### Utility Libraries
- **urllib.parse**: URL validation and parsing
- **base64**: File encoding for download links
- **json**: Data serialization and configuration storage
- **datetime**: Timestamp management and scheduling calculations

### Environment Configuration
- **os**: Environment variable access for secure credential management
- Application requires ADMIN_USERNAME and ADMIN_PASSWORD environment variables for security