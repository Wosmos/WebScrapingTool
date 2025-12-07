"""
Modern FastAPI Web Scraper Application
Built with contemporary design and proper separation of UI from logic
"""

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from datetime import datetime, timedelta
from database import ScrapingDatabase
from web_scraper import get_website_text_content
from typing import Optional
import secrets

# Initialize FastAPI app
app = FastAPI(title="Smart Web Scraper API", description="Modern web scraping API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
db = ScrapingDatabase()

# Admin credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'your_username')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'your_secure_password')

# Session storage (in production, use Redis or database)
sessions = {}

# Token expiry time
TOKEN_EXPIRY_HOURS = 24

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class ScrapeRequest(BaseModel):
    url: str
    respect_robots: bool = True

class ScrapeBatchRequest(BaseModel):
    urls: list[str]
    respect_robots: bool = True

# Authentication dependency
async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    if token not in sessions:
        return None
    
    session = sessions[token]
    # Check if token expired
    if datetime.now() > session.get("expires_at", datetime.now()):
        del sessions[token]
        return None
    
    return session

async def require_auth(request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

# Routes
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Smart Web Scraper API",
        "version": "2.0",
        "docs": "/docs"
    }

@app.post("/api/login")
async def login_api(login_data: LoginRequest):
    """Login API endpoint - returns JWT-like token"""
    if login_data.username == ADMIN_USERNAME and login_data.password == ADMIN_PASSWORD:
        # Create session token
        token = secrets.token_urlsafe(32)
        sessions[token] = {
            "username": login_data.username,
            "authenticated": True,
            "login_time": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        }
        
        return {
            "success": True, 
            "message": "Login successful",
            "token": token,
            "username": login_data.username,
            "expires_in": TOKEN_EXPIRY_HOURS * 3600  # seconds
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/dashboard")
async def dashboard(user = Depends(require_auth)):
    """Get dashboard data"""
    recent_sessions = db.get_sessions()[:6]
    return {
        "user": user,
        "recent_sessions": recent_sessions
    }

@app.get("/api/sessions")
async def get_all_sessions(user = Depends(require_auth)):
    """Get all scraping sessions"""
    sessions_data = db.get_sessions()
    return {
        "sessions": sessions_data
    }

@app.post("/api/scrape")
async def scrape_single_url(request: Request, scrape_data: ScrapeRequest, user = Depends(require_auth)):
    """API endpoint for single URL scraping"""
    try:
        # Start scraping session
        session_id = db.create_session(f"Single URL: {scrape_data.url}", 1)
        
        # Extract content
        content = get_website_text_content(scrape_data.url)
        
        if content:
            # Store the result
            db.save_scraped_data(session_id, scrape_data.url, content, title=scrape_data.url)
            
            # Calculate metrics
            word_count = len(content.split()) if content else 0
            char_count = len(content) if content else 0
            line_count = len(content.splitlines()) if content else 0
            
            return JSONResponse({
                "success": True,
                "session_id": session_id,
                "content": content,
                "url": scrape_data.url,
                "metrics": {
                    "word_count": word_count,
                    "char_count": char_count,
                    "line_count": line_count,
                    "timestamp": datetime.now().isoformat()
                }
            })
        else:
            return JSONResponse({
                "success": False,
                "error": "Failed to extract content from URL"
            }, status_code=400)
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Scraping failed: {str(e)}"
        }, status_code=500)

@app.post("/api/scrape/batch")
async def scrape_batch_urls(request: Request, batch_data: ScrapeBatchRequest, user = Depends(require_auth)):
    """API endpoint for batch URL scraping"""
    try:
        # Start scraping session
        session_id = db.create_session(f"Batch: {len(batch_data.urls)} URLs", len(batch_data.urls))
        results = []
        
        for url in batch_data.urls:
            try:
                content = get_website_text_content(url)
                if content:
                    db.save_scraped_data(session_id, url, content, title=url)
                    results.append({
                        "url": url,
                        "success": True,
                        "word_count": len(content.split()),
                        "char_count": len(content)
                    })
                else:
                    results.append({
                        "url": url,
                        "success": False,
                        "error": "No content extracted"
                    })
            except Exception as e:
                results.append({
                    "url": url,
                    "success": False,
                    "error": str(e)
                })
        
        return JSONResponse({
            "success": True,
            "session_id": session_id,
            "results": results,
            "total_urls": len(batch_data.urls),
            "successful": len([r for r in results if r["success"]])
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Batch scraping failed: {str(e)}"
        }, status_code=500)

@app.get("/api/session/{session_id}")
async def get_session_data(session_id: int, user = Depends(require_auth)):
    """Get session data"""
    try:
        session_data = db.get_session_data(session_id)
        if session_data:
            return JSONResponse(session_data)
        else:
            return JSONResponse({"error": "Session not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/logout")
async def logout(request: Request):
    """Logout endpoint"""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        if token in sessions:
            del sessions[token]
    
    return {"success": True, "message": "Logged out successfully"}

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)