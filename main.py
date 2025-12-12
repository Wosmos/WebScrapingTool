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
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3000"],  # Next.js dev server
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
            
            # Mark session as completed
            db.complete_session(session_id)
            
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
            db.save_scraped_data(session_id, scrape_data.url, "", title=scrape_data.url, status="failed", error_message="Failed to extract content")
            db.complete_session(session_id)
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
                    db.save_scraped_data(session_id, url, "", title=url, status="failed", error_message="No content extracted")
                    results.append({
                        "url": url,
                        "success": False,
                        "error": "No content extracted"
                    })
            except Exception as e:
                db.save_scraped_data(session_id, url, "", title=url, status="failed", error_message=str(e))
                results.append({
                    "url": url,
                    "success": False,
                    "error": str(e)
                })
        
        # Mark session as completed
        db.complete_session(session_id)
        
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


@app.get("/api/session/{session_id}/export/csv")
async def export_csv(session_id: int, user = Depends(require_auth)):
    """Export session data as CSV"""
    from fastapi.responses import StreamingResponse
    import io
    import csv
    
    try:
        session_data = db.get_session_data(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['URL', 'Title', 'Word Count', 'Char Count', 'Scraped At', 'Status'])
        
        # Write data
        for item in session_data['data']:
            writer.writerow([
                item['url'],
                item['title'] or '',
                item['word_count'],
                item['char_count'],
                item['scraped_at'],
                item['status']
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=session_{session_id}.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}/export/excel")
async def export_excel(session_id: int, user = Depends(require_auth)):
    """Export session data as Excel"""
    from fastapi.responses import StreamingResponse
    import io
    import pandas as pd
    
    try:
        session_data = db.get_session_data(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create DataFrame
        df_data = []
        for item in session_data['data']:
            df_data.append({
                'URL': item['url'],
                'Title': item['title'] or '',
                'Content Preview': item['content'][:200] if item['content'] else '',
                'Word Count': item['word_count'],
                'Char Count': item['char_count'],
                'Scraped At': item['scraped_at'],
                'Status': item['status']
            })
        
        df = pd.DataFrame(df_data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Scraped Data')
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=session_{session_id}.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}/export/pdf")
async def export_pdf(session_id: int, user = Depends(require_auth)):
    """Export session data as PDF"""
    from fastapi.responses import StreamingResponse
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    import io
    
    try:
        session_data = db.get_session_data(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=30,
        )
        elements.append(Paragraph(f"Scraping Session Report", title_style))
        elements.append(Spacer(1, 12))
        
        # Session info
        session_info = session_data['session']
        info_data = [
            ['Session Name:', session_info['name']],
            ['Created:', str(session_info['created_at'])],
            ['Total URLs:', str(session_info['total_urls'])],
            ['Status:', session_info['status']],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        # Data table
        elements.append(Paragraph("Scraped URLs", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        table_data = [['URL', 'Words', 'Chars', 'Status']]
        for item in session_data['data']:
            url_text = item['url'][:50] + '...' if len(item['url']) > 50 else item['url']
            table_data.append([
                url_text,
                str(item['word_count']),
                str(item['char_count']),
                item['status']
            ])
        
        data_table = Table(table_data, colWidths=[3.5*inch, 1*inch, 1*inch, 1*inch])
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(data_table)
        
        doc.build(elements)
        buffer.seek(0)
        
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=session_{session_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: int, user = Depends(require_auth)):
    """Delete a session"""
    try:
        db.delete_session(session_id)
        return {"success": True, "message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
