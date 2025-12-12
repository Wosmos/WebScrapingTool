# Quick Start Guide

## 🚀 Your Application is Running!

### Services Status
✅ **Backend API**: http://localhost:5000  
✅ **Frontend**: http://localhost:3000

## 📝 How to Use

### 1. Access the Application
Open your browser and go to: **http://localhost:3000**

### 2. Login
- Click "Get Started" on the landing page
- Default credentials:
  - Username: `your_username`
  - Password: `your_secure_password`
  
  ⚠️ **Change these in your environment variables!**

### 3. Features Available

#### 🔍 Single URL Scraper
- Navigate to "Single URL Scraper" from dashboard
- Enter any website URL
- Click "Scrape URL"
- View extracted content and metrics

#### 📦 Batch Scraper
- Navigate to "Batch Scraper"
- Enter multiple URLs (one per line)
- Click "Scrape All URLs"
- See results for each URL

#### 📊 History
- View all past scraping sessions
- See metrics and timestamps

## 🛠️ Development

### Backend (FastAPI)
```bash
# Running on http://localhost:5000
# API docs available at: http://localhost:5000/docs
```

### Frontend (Next.js)
```bash
# Running on http://localhost:3000
cd frontend
npm run dev
```

## 🔧 Configuration

### Change Admin Credentials
Set environment variables:
```bash
# Windows
set ADMIN_USERNAME=your_new_username
set ADMIN_PASSWORD=your_new_password

# Linux/Mac
export ADMIN_USERNAME=your_new_username
export ADMIN_PASSWORD=your_new_password
```

### Change API URL (Frontend)
Edit `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## 📚 API Documentation

FastAPI provides interactive API docs:
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Next.js       │  HTTP   │   FastAPI       │
│   Frontend      │ ◄─────► │   Backend       │
│   (Port 3000)   │  REST   │   (Port 5000)   │
└─────────────────┘         └─────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   SQLite DB     │
                            └─────────────────┘
```

## 🎯 Key Improvements

### Before (Monolithic)
- ❌ HTML templates mixed with Python
- ❌ Server-side rendering only
- ❌ Harder to scale
- ❌ Limited UI capabilities

### After (Microservices)
- ✅ Clean separation of concerns
- ✅ Modern React UI with TypeScript
- ✅ Independent scaling
- ✅ Better developer experience
- ✅ API-first architecture
- ✅ Easy to add more services

## 🚢 Deployment

### Frontend (Vercel - Recommended)
```bash
cd frontend
vercel deploy
```

### Backend (Railway/Render)
```bash
# Push to GitHub
# Connect to Railway/Render
# Set environment variables
# Deploy!
```

## 🔒 Security Notes

1. **Change default credentials** immediately
2. **Use HTTPS** in production
3. **Update CORS origins** for production domains
4. **Use environment variables** for secrets
5. **Add rate limiting** for production

## 📞 Support

For issues or questions, check:
- `ARCHITECTURE.md` - Detailed architecture docs
- `README.md` - Original project documentation
- FastAPI docs: http://localhost:5000/docs

## 🎉 Next Steps

1. Customize the UI in `frontend/app/`
2. Add more API endpoints in `main.py`
3. Enhance scraping logic in `web_scraper.py`
4. Add authentication providers (OAuth, etc.)
5. Implement real-time updates with WebSockets
6. Add export functionality (CSV, PDF, Excel)
7. Deploy to production!

---

**Enjoy your modern microservice architecture! 🚀**
