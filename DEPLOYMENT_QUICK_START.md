# Deployment Quick Start Guide
# For the AI Palmistry & Tarot Intelligence Platform

## Critical Steps Before Any Deployment

### 1. Apply Code Fixes (Required - ~1 hour)

#### Fix database.py
Location: `backend/app/database.py`

Remove this line:
```python
DATABASE_URL = "postgresql+psycopg2://postgres:Maria15@localhost:5432/ai_palmistry"
```

Replace with:
```python
from app.config import DATABASE_URL
```

#### Fix main.py CORS
Location: `backend/app/main.py` (lines 31-36)

Replace:
```python
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
```

With:
```python
import os
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
```

#### Fix frontend api.js
Location: `frontend/src/services/api.js`

Replace:
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000';
```

With:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
```

#### Fix hardcoded calls in components
Files:
- `frontend/src/pages/AIDashboard.jsx` (line 12)
- `frontend/src/pages/ThreeCardHistory.jsx` (line 42)

Replace all instances of:
```javascript
axios.get('http://127.0.0.1:8000/...
```

With:
```javascript
import api from '../services/api';
api.get('/...
```

#### Add Gunicorn to backend/requirements.txt
Add these lines:
```
gunicorn==21.2.0
uvicorn[standard]==0.49.0
```

### 2. Set Up Environment Files

#### backend/.env (IMPORTANT: Never commit this)
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_palmistry
SECRET_KEY=[GENERATE_NEW_KEY]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=[YOUR_GEMINI_KEY]
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### frontend/.env.local (for development, never commit)
```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

#### Update .gitignore
Add:
```
backend/.env
frontend/.env.local
frontend/.env.*.local
```

### 3. Choose Deployment Platform

**RECOMMENDED: Render.com**

Reasons:
- Free PostgreSQL database
- Simple deployment
- Automatic HTTPS/SSL
- Free tier for testing
- $7/month for backend service

**Alternative:** Railway, Supabase, or Fly.io

### 4. Deploy Backend (Render.com Instructions)

1. Create PostgreSQL database:
   - Go to render.com dashboard
   - Create new PostgreSQL instance
   - Copy connection string

2. Deploy backend service:
   - Create new "Web Service"
   - Connect GitHub repo
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 app.main:app`

3. Add environment variables:
   ```
   DATABASE_URL=[Your PostgreSQL connection string]
   SECRET_KEY=[Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"]
   GEMINI_API_KEY=[Your Gemini API key]
   FRONTEND_URL=https://your-frontend-domain.com
   CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
   ```

4. Deploy backend - note your backend URL (e.g., https://api-domain.render.com)

### 5. Deploy Frontend (Render.com Instructions)

1. Create Static Site:
   - Create new "Static Site"
   - Connect GitHub repo
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`

2. Add environment variables:
   ```
   VITE_API_BASE_URL=https://your-backend-domain.render.com
   ```

3. Deploy frontend - note your frontend URL

4. Update backend environment:
   - Edit backend Web Service
   - Update FRONTEND_URL to new frontend URL
   - Update CORS_ORIGINS to new frontend URL
   - Redeploy backend

### 6. Testing Checklist

- [ ] Frontend loads without errors
- [ ] User can register
- [ ] User can login
- [ ] User can upload palm image
- [ ] Palm analysis completes successfully
- [ ] User can request tarot reading
- [ ] PDF report generation works
- [ ] No CORS errors in browser console
- [ ] API responses are fast (<500ms)

### 7. Database Setup

Current approach: Tables auto-create on backend startup

If needed later, migrate to Alembic:
```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## Local Testing Before Production Deployment

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Edit .env with local PostgreSQL credentials

# Start backend
python -m uvicorn app.main:app --reload

# Frontend setup (in new terminal)
cd frontend
npm install
npm run dev

# Test at http://localhost:5173
```

---

## Production Deployment Commands

### Backend
```bash
gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 app.main:app
```

### Frontend Build
```bash
cd frontend
npm install
npm run build
# Output: dist/
```

---

## Key Files Modified for Deployment

1. ✅ `backend/app/database.py` - Remove hardcoded URL
2. ✅ `backend/app/main.py` - Use env var for CORS
3. ✅ `backend/requirements.txt` - Add gunicorn
4. ✅ `backend/.env.example` - Created
5. ✅ `frontend/src/services/api.js` - Use env var
6. ✅ `frontend/.env.example` - Created
7. ✅ `.gitignore` - Update to exclude .env files

---

## Support & Troubleshooting

### Backend won't start
- Check DATABASE_URL is valid
- Verify PostgreSQL is running (dev) or accessible (production)
- Check all required env vars are set
- Review logs: `render logs` or platform's log viewer

### Frontend can't connect to API
- Check VITE_API_BASE_URL is correct
- Verify backend CORS_ORIGINS includes frontend domain
- Check browser console for errors
- Ensure backend is actually running

### Database errors
- Verify connection string format
- Check credentials are correct
- Verify database exists
- Check firewall/network access (production)

---

## Estimated Cost (Monthly)

| Service | Cost | Notes |
|---------|------|-------|
| Render PostgreSQL | $15 | Can start free, upgrade as needed |
| Backend Service | $7 | Can start free tier |
| Frontend Static | $0 | Free tier sufficient |
| **TOTAL** | $22 | Minimum viable production |

---

## For More Details

See: `DEPLOYMENT_READINESS_ANALYSIS.md` in the project root.

---

**Last Updated:** August 12, 2026
**Status:** Ready for production deployment after fixes applied
