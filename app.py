import streamlit as st
import pandas as pd
import base64
import re
from urllib.parse import urlparse
from web_scraper import get_website_text_content
import time

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

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
        # Convert text to CSV format (simple single column)
        df = pd.DataFrame({"Scraped Content": [data]})
        csv_string = df.to_csv(index=False)
        b64 = base64.b64encode(csv_string.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download as CSV</a>'
    else:
        # Text file download
        b64 = base64.b64encode(data.encode()).decode()
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
        page = st.selectbox("Select Page", ["Scraper", "About"])
    
    # Main content area
    if page == "Scraper":
        scraper_page()
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
