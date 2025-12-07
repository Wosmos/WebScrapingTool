# Modern Microservice Architecture

## Overview
This project has been refactored into a modern microservice architecture with:
- **Frontend**: Next.js 15 with TypeScript and Tailwind CSS
- **Backend**: FastAPI (Python) with CORS support
- **Database**: SQLite (can be upgraded to PostgreSQL)

## Architecture Benefits

### Separation of Concerns
- Frontend and backend are completely decoupled
- Each service can be developed, tested, and deployed independently
- Clear API contracts between services

### Scalability
- Frontend and backend can scale independently
- Easy to add more microservices (e.g., notification service, analytics service)
- Can deploy to different servers/containers

### Modern Tech Stack
- **Next.js**: Server-side rendering, routing, and optimizations
- **TypeScript**: Type safety and better developer experience
- **Tailwind CSS**: Utility-first CSS for rapid UI development
- **FastAPI**: High-performance async Python framework

## Project Structure

```
.
├── frontend/                 # Next.js Frontend
│   ├── app/                 # App router pages
│   │   ├── page.tsx        # Landing page
│   │   ├── login/          # Login page
│   │   ├── dashboard/      # Dashboard
│   │   ├── scraper/        # Single URL scraper
│   │   ├── batch/          # Batch scraper
│   │   └── history/        # History page
│   ├── lib/                # Utilities
│   │   └── api.ts          # API client
│   └── .env.local          # Environment variables
│
├── main.py                  # FastAPI backend (API only)
├── database.py              # Database operations
├── web_scraper.py           # Scraping logic
└── scheduler.py             # Background tasks

```

## Running the Application

### Backend (FastAPI)
```bash
# Already running on http://localhost:5000
python main.py
```

### Frontend (Next.js)
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

## API Endpoints

### Authentication
- `POST /api/login` - Login and get token
- `POST /api/logout` - Logout

### Scraping
- `POST /api/scrape` - Scrape single URL
- `POST /api/scrape/batch` - Scrape multiple URLs
- `GET /api/session/{id}` - Get session data

### Dashboard
- `GET /api/dashboard` - Get dashboard data
- `GET /api/sessions` - Get all sessions

## Authentication Flow

1. User logs in via `/login` page
2. Frontend sends credentials to `/api/login`
3. Backend returns JWT-like token
4. Frontend stores token in localStorage
5. All subsequent requests include `Authorization: Bearer <token>` header
6. Backend validates token on protected routes

## Environment Variables

### Backend (.env or system env)
```
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_secure_password
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Deployment Options

### Option 1: Separate Deployments
- **Frontend**: Vercel, Netlify, or any static hosting
- **Backend**: Railway, Render, AWS, or any Python hosting

### Option 2: Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5000:5000"
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:5000
```

### Option 3: Kubernetes
Deploy as separate microservices with proper service discovery

## Future Enhancements

1. **Add Redis** for session management
2. **PostgreSQL** for production database
3. **WebSocket** for real-time scraping updates
4. **Message Queue** (RabbitMQ/Kafka) for async processing
5. **API Gateway** for routing and rate limiting
6. **Monitoring** with Prometheus/Grafana
7. **CI/CD** pipeline with GitHub Actions

## Development

### Backend Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --port 5000
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Testing

### Backend
```bash
# Run tests
pytest

# Test API endpoints
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

### Frontend
```bash
cd frontend
npm test
```

## Security Considerations

1. **CORS**: Configured for localhost:3000 (update for production)
2. **Token Expiry**: Tokens expire after 24 hours
3. **HTTPS**: Use HTTPS in production
4. **Environment Variables**: Never commit secrets
5. **Rate Limiting**: Add rate limiting for production

## Performance

- **Frontend**: Static generation where possible
- **Backend**: Async operations with FastAPI
- **Caching**: Add Redis for frequently accessed data
- **CDN**: Use CDN for frontend assets in production
