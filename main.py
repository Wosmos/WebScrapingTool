"""
Modern FastAPI Web Scraper Application
Built with contemporary design and proper separation of UI from logic
"""

from fastapi import FastAPI, Request, Depends, HTTPException, Form, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
import asyncio
from datetime import datetime
from database import ScrapingDatabase
from web_scraper import get_website_text_content
import json
import traceback
from typing import Optional

# Initialize FastAPI app
app = FastAPI(title="Smart Web Scraper", description="Modern web scraping platform")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Database
db = ScrapingDatabase()

# Admin credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'your_username')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'your_secure_password')

# Session storage (in production, use Redis or database)
sessions = {}

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
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return None
    return sessions[session_id]

async def require_auth(request: Request):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

# Routes
@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Modern landing page"""
    user = await get_current_user(request)
    return templates.TemplateResponse("landing.html", {
        "request": request, 
        "user": user
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Modern login page"""
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.post("/api/login")
async def login_api(request: Request, login_data: LoginRequest):
    """Login API endpoint"""
    if login_data.username == ADMIN_USERNAME and login_data.password == ADMIN_PASSWORD:
        # Create session
        session_id = f"session_{datetime.now().timestamp()}"
        sessions[session_id] = {
            "username": login_data.username,
            "authenticated": True,
            "login_time": datetime.now()
        }
        
        response = JSONResponse({
            "success": True, 
            "message": "Login successful",
            "redirect": "/dashboard"
        })
        response.set_cookie("session_id", session_id, httponly=True, max_age=86400)
        return response
    else:
        return JSONResponse({
            "success": False, 
            "message": "Invalid credentials"
        }, status_code=401)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user = Depends(require_auth)):
    """Modern dashboard"""
    recent_sessions = db.get_sessions()[:6]  # Get first 6 sessions
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "recent_sessions": recent_sessions
    })

@app.get("/scraper", response_class=HTMLResponse)
async def scraper_page(request: Request, user = Depends(require_auth)):
    """Modern scraper interface"""
    return templates.TemplateResponse("scraper.html", {
        "request": request,
        "user": user
    })

@app.get("/batch", response_class=HTMLResponse)
async def batch_scraper_page(request: Request, user = Depends(require_auth)):
    """Batch scraping interface"""
    return templates.TemplateResponse("batch.html", {
        "request": request,
        "user": user
    })

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, user = Depends(require_auth)):
    """Scraping history page"""
    sessions_data = db.get_sessions()
    return templates.TemplateResponse("history.html", {
        "request": request,
        "user": user,
        "sessions": sessions_data
    })

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

@app.post("/logout")
async def logout(request: Request):
    """Logout endpoint"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        del sessions[session_id]
    
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session_id")
    return response

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)