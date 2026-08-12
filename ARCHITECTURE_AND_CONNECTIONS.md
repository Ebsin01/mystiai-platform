# Architecture & Connection Mapping
## AI Palmistry & Tarot Intelligence Platform

---

## 1. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRODUCTION DEPLOYMENT                        │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ FRONTEND TIER (Static Site / Web Service)                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  React 19.2.7 + Vite 8.1.1 + Tailwind CSS                          │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │  src/                                                    │        │
│  │  ├── pages/                                             │        │
│  │  │   ├── TarotReading.jsx                              │        │
│  │  │   ├── PalmAnalysis.jsx                              │        │
│  │  │   └── AIDashboard.jsx                               │        │
│  │  └── services/                                         │        │
│  │      └── api.js (VITE_API_BASE_URL)                   │        │
│  └─────────────────────────────────────────────────────────┘        │
│                                                                       │
│  Domain: https://your-frontend-domain.com                           │
│  Port: 443 (HTTPS)                                                  │
│  Build: npm run build → dist/                                       │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                HTTP/HTTPS CORS     │ Accept-Origin: https://your-frontend-domain.com
                  JSON Requests     │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ API BACKEND TIER (FastAPI Web Service)                              │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  FastAPI 0.139.0 + Uvicorn 0.49.0 + Gunicorn                       │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │  app/                                                    │        │
│  │  ├── main.py                                            │        │
│  │  │   ├── CORS Middleware (CORS_ORIGINS env)           │        │
│  │  │   ├── Database initialization                       │        │
│  │  │   └── Routes registration                           │        │
│  │  ├── config.py                                          │        │
│  │  │   ├── DATABASE_URL (env var)                        │        │
│  │  │   ├── SECRET_KEY (env var)                          │        │
│  │  │   ├── GEMINI_API_KEY (env var)                      │        │
│  │  │   └── Validation on startup                         │        │
│  │  ├── database.py                                        │        │
│  │  │   └── SQLAlchemy engine                             │        │
│  │  ├── routers/                                          │        │
│  │  │   ├── auth.py (login, register, profile)           │        │
│  │  │   ├── palm.py (palm analysis endpoints)            │        │
│  │  │   ├── tarot.py (tarot reading endpoints)           │        │
│  │  │   ├── reports.py (report generation)               │        │
│  │  │   └── notifications.py                              │        │
│  │  └── services/                                         │        │
│  │      ├── gemini_service.py (AI interpretation)        │        │
│  │      ├── palm_analysis_engine.py                      │        │
│  │      └── [other services]                              │        │
│  └─────────────────────────────────────────────────────────┘        │
│                                                                       │
│  Domain: https://your-backend-domain.com                            │
│  Port: 443 (HTTPS) - Reverse proxy to 8000                         │
│  Start: gunicorn --workers 4 ...                                    │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                   SQL Queries      │ psycopg2 driver
                   Connection Pool  │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ DATABASE TIER (PostgreSQL Managed Service)                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  PostgreSQL 13+ (Render / Railway / Supabase)                       │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │  Tables:                                                │        │
│  │  ├── users (authentication & authorization)            │        │
│  │  ├── palm_analyses (palm analysis results)            │        │
│  │  ├── palm_interpretations (detailed interpretations)  │        │
│  │  ├── tarot_cards (tarot card definitions)             │        │
│  │  ├── three_card_readings (tarot reading results)      │        │
│  │  ├── personality_reports (generated reports)          │        │
│  │  └── notifications (user notifications)                │        │
│  └─────────────────────────────────────────────────────────┘        │
│                                                                       │
│  Connection: postgresql://user:password@host:5432/dbname           │
│  Port: 5432                                                         │
│  Backup: Automated (managed service)                                │
│  SSL: Required for production connections                          │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                   REST API Calls   │ Google Gemini Client
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ EXTERNAL SERVICES                                                    │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. Google Gemini AI Service                                        │
│     ├── Endpoint: https://generativelanguage.googleapis.com         │
│     ├── Authentication: GEMINI_API_KEY (API key)                    │
│     └── Purpose: AI-powered personality & reading interpretations   │
│                                                                       │
│  2. File Storage (Palm images, reports)                             │
│     ├── Location: /backend/uploads/palms/                           │
│     ├── Type: Local filesystem (for MVP)                            │
│     └── Production: Should migrate to S3/Render file system         │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. Environment Variables Mapping

### Backend Environment Variables (`backend/.env`)

| Variable | Purpose | Example | Source |
|----------|---------|---------|--------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` | Config management |
| `SECRET_KEY` | JWT signing key | `[32+ random chars]` | Generated at setup |
| `ALGORITHM` | JWT algorithm | `HS256` | Fixed value |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `60` | Configuration |
| `GEMINI_API_KEY` | Google AI API key | `AIza...` | Google Cloud Console |
| `FRONTEND_URL` | Frontend domain | `https://domain.com` | Deployment config |
| `CORS_ORIGINS` | Allowed CORS origins | `https://domain.com,...` | Deployment config |

### Frontend Environment Variables (`frontend/.env.local` or build-time)

| Variable | Purpose | Example | Source |
|----------|---------|---------|--------|
| `VITE_API_BASE_URL` | Backend API endpoint | `https://api.domain.com` | Build config |

### Environment Variable Dependency Chain

```
Configuration Hierarchy:
├── Local Development (.env files)
├── Platform Dashboard (Render, Railway, etc.)
└── Secrets Management (later: HashiCorp Vault, AWS Secrets Manager)

Data Flow:
├── Backend startup
│   ├── Loads .env via python-dotenv
│   ├── config.py validates all required vars
│   └── database.py uses DATABASE_URL from config
│
└── Frontend build
    ├── Vite injects VITE_* variables
    ├── api.js reads VITE_API_BASE_URL
    └── Build-time substitution (not runtime)
```

---

## 3. Connection Flow: Request/Response Cycles

### Authentication Flow

```
1. USER REGISTRATION
   ┌─────────────┐
   │   Frontend  │
   │ (register)  │
   └──────┬──────┘
          │ POST /register
          │ {"email": "...", "password": "..."}
          ▼
   ┌──────────────────────┐
   │  Backend: auth.py    │
   │ 1. Hash password     │
   │ 2. Create User row   │
   │ 3. Return success    │
   └──────┬───────────────┘
          │
          ▼
   ┌──────────────────────┐
   │   PostgreSQL DB      │
   │   INSERT users ...   │
   └──────────────────────┘

2. USER LOGIN
   ┌─────────────┐
   │   Frontend  │
   │  (login)    │
   └──────┬──────┘
          │ POST /login
          │ {"username": "...", "password": "..."}
          ▼
   ┌──────────────────────┐
   │  Backend: auth.py    │
   │ 1. Find user         │
   │ 2. Verify password   │
   │ 3. Generate JWT      │
   │ 4. Return token      │
   └──────┬───────────────┘
          │ {"access_token": "eyJ..."}
          ▼
   ┌─────────────────────────┐
   │   Frontend              │
   │ Save token to localStorage
   └─────────────────────────┘

3. AUTHENTICATED REQUEST
   ┌──────────────────────┐
   │   Frontend           │
   │ GET /palm/history    │
   │ Authorization: Bearer eyJ...
   └──────┬───────────────┘
          │
          ▼
   ┌──────────────────────────┐
   │  Backend: dependency.py  │
   │ 1. Extract JWT token     │
   │ 2. Verify signature      │
   │ 3. Decode payload        │
   │ 4. Find user in DB       │
   │ 5. Return user object    │
   └──────┬───────────────────┘
          │ Passed to route handler
          ▼
   ┌──────────────────────┐
   │  Backend: palm.py    │
   │ Return user's analyses
   └──────┬───────────────┘
          │
          ▼
   ┌──────────────────────┐
   │   PostgreSQL DB      │
   │   SELECT * FROM      │
   │   palm_analyses      │
   │   WHERE user_id = ?  │
   └──────────────────────┘
```

### Palm Analysis Flow

```
1. USER UPLOADS PALM IMAGE
   ┌─────────────┐
   │   Frontend  │
   │ Upload form │
   └──────┬──────┘
          │ POST /palm/analyze (multipart/form-data)
          │ file: [image data]
          │ Authorization: Bearer [token]
          ▼
   ┌────────────────────────────┐
   │  Backend: palm.py router   │
   │ 1. Validate auth token     │
   │ 2. Receive image file      │
   │ 3. Save to uploads/palms/  │
   │ 4. Call analysis engine    │
   └──────┬─────────────────────┘
          │
          ▼
   ┌────────────────────────────┐
   │ palm_analysis_engine.py    │
   │ (MediaPipe + TensorFlow)   │
   │ 1. Extract palm features   │
   │ 2. Run ML model            │
   │ 3. Get prediction scores   │
   └──────┬─────────────────────┘
          │
          ▼
   ┌────────────────────────────┐
   │ gemini_service.py          │
   │ 1. Prepare prompt          │
   │ 2. Call Google Gemini API  │
   │ 3. Get AI interpretation   │
   └──────┬─────────────────────┘
          │ HTTPS to Google
          ▼
   ┌────────────────────────────┐
   │ Google Gemini API          │
   │ Return: {"personality...  │
   └────────────────────────────┘

2. SAVE ANALYSIS RESULTS
   ┌────────────────────────────┐
   │ Backend: palm.py router    │
   │ 1. Create PalmAnalysis row │
   │ 2. Create Interpretation   │
   │ 3. Return results          │
   └──────┬─────────────────────┘
          │
          ▼
   ┌────────────────────────────┐
   │   PostgreSQL DB            │
   │ INSERT palm_analyses ...   │
   │ INSERT interpretations ... │
   └────────────────────────────┘

3. RETURN TO FRONTEND
   ┌────────────────────────────┐
   │  Backend Response          │
   │ {"id": 123, "scores": {...}│
   └──────┬─────────────────────┘
          │
          ▼
   ┌─────────────┐
   │   Frontend  │
   │ Display     │
   │ results     │
   └─────────────┘
```

---

## 4. Database Schema Overview

### Table Relationships

```
users (1) ─────────────────────┐
  ├─ id (PK)                    │ One-to-Many
  ├─ email (UNIQUE)             │
  ├─ password (hashed)          │
  ├─ role (User/Admin)          │
  └─ created_at                 │
                                │
                  ┌─────────────┤
                  │             │
                  ▼             ▼
        palm_analyses      tarot_readings
        ├─ id (PK)         ├─ id (PK)
        ├─ user_id (FK)    ├─ user_id (FK)
        ├─ image_path      ├─ question
        ├─ scores: {}      └─ ...
        └─ created_at
           │
           │ One-to-One
           ▼
      palm_interpretations
      ├─ id (PK)
      ├─ analysis_id (FK)
      ├─ personality_type
      ├─ strengths
      ├─ weaknesses
      └─ ...

      three_card_readings
      ├─ id (PK)
      ├─ user_id (FK)
      ├─ card_1_id
      ├─ card_2_id
      ├─ card_3_id
      └─ interpretation

tarot_cards (Reference)
      ├─ id (PK)
      ├─ name
      ├─ meaning
      └─ image_url

personality_reports (Generated)
      ├─ id (PK)
      ├─ user_id (FK)
      ├─ analysis_id (FK)
      ├─ content (PDF)
      └─ generated_at

notifications (Async)
      ├─ id (PK)
      ├─ user_id (FK)
      ├─ message
      ├─ read
      └─ created_at
```

---

## 5. API Endpoint Mapping

### Authentication Endpoints
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/register` | POST | ❌ | User registration |
| `/login` | POST | ❌ | User login (returns JWT) |
| `/profile` | GET | ✅ | Get current user profile |
| `/admin` | GET | ✅ Admin | Admin dashboard access |

### Palm Analysis Endpoints
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/palm/analyze` | POST | ✅ | Submit palm image for analysis |
| `/palm/analyses` | GET | ✅ | Get user's analysis history |
| `/palm/analyses/{id}` | GET | ✅ | Get specific analysis details |
| `/palm/analyses/{id}` | DELETE | ✅ | Delete analysis |

### Tarot Endpoints
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/tarot/three-card-readings` | GET | ✅ | Get reading history |
| `/tarot/three-card-readings` | POST | ✅ | Create new reading |
| `/tarot/three-card-readings/{id}` | GET | ✅ | Get specific reading |

### Reports Endpoints
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/reports/personality` | POST | ✅ | Generate personality report |
| `/reports/{id}/download` | GET | ✅ | Download PDF report |

### System Endpoints
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/` | GET | ❌ | Health check |
| `/ai/model-info` | GET | ❌ | Get AI model metadata |
| `/debug` | GET | ❌ | Debug info (remove in production) |

---

## 6. Technology Stack Details

### Backend Stack
```
FastAPI 0.139.0
├── Web Framework: async Python web server
├── Routing: auto-generated OpenAPI docs
├── Validation: Pydantic models
└── CORS: FastAPI middleware

SQLAlchemy 2.0.51
├── ORM: Object-relational mapping
├── Database abstraction: Driver-agnostic
└── Relationships: Foreign keys, cascades

psycopg2-binary 2.9.12
├── PostgreSQL driver: Native C implementation
├── Connection pooling: Configurable
└── Async support: Compatible with asyncpg

Authentication:
├── JWT (json Web Tokens): python-jose
├── Password hashing: bcrypt via passlib
├── OAuth2 scheme: Bearer tokens
└── Expiring tokens: Configurable TTL

AI Services:
├── Google Gemini: google-genai 2.17.0
├── Palm Detection: MediaPipe 0.10.32
├── ML Models: TensorFlow-CPU 2.15.0
└── Image Processing: OpenCV-Python-Headless

PDF Generation:
└── ReportLab: For report PDF creation
```

### Frontend Stack
```
React 19.2.7
├── Component-based UI
├── Hooks for state management
└── React Router v7.18.1 for routing

Vite 8.1.1
├── Build tool: Lightning-fast builds
├── Dev server: Hot module replacement
├── Environment variables: VITE_* prefix
└── Output: Static HTML/CSS/JS in dist/

Tailwind CSS 4.3.2
├── Utility-first CSS
├── Responsive design
└── Custom styling

Axios 1.18.1
├── HTTP client: Promise-based
├── Interceptors: Auto-inject auth tokens
├── Request/response handling
└── Error management

Other:
├── JWT Decode: Parsing tokens on client
└── React Router DOM: Client-side navigation
```

### Database Stack
```
PostgreSQL 13+
├── ACID compliance
├── JSON support
├── Full-text search
├── Scalability
└── Mature production database

Managed Providers:
├── Render PostgreSQL: Recommended for MVP
├── Railway PostgreSQL: Good alternative
├── Supabase: Extra features included
└── Neon: Serverless option

Connection Details:
├── Driver: psycopg2
├── Default Port: 5432
├── SSL: Required in production
├── Connection string format:
│   postgresql://user:password@host:port/database
```

---

## 7. Deployment Environment Variables Summary

### Production Deployment (Example: Render.com)

**Database Service:**
```
Type: PostgreSQL
Host: [render-host].render.com
Port: 5432
Database: [auto-generated]
Username: [auto-generated]
Password: [auto-generated]
Connection String: postgresql://...
```

**Backend Service:**
```
Environment variables:
  DATABASE_URL=postgresql://user:pass@render.com:5432/db
  SECRET_KEY=[generated-secure-key]
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=60
  GEMINI_API_KEY=[your-gemini-key]
  FRONTEND_URL=https://your-frontend-domain.com
  CORS_ORIGINS=https://your-frontend-domain.com

Build: pip install -r requirements.txt
Start: gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 app.main:app
```

**Frontend Service:**
```
Environment variables:
  VITE_API_BASE_URL=https://your-backend-domain.com

Build: cd frontend && npm install && npm run build
Output: frontend/dist/
```

---

## 8. Data Flow Diagrams

### Complete Request Lifecycle (Example: Palm Analysis)

```
Time: T0 ─────────────────────────────────────────────────► T0+30s

T0: User Action
   ├─ Click "Upload Palm"
   └─ Select image file

T0+100ms: Frontend
   ├─ Validate file (type, size)
   ├─ Show loading spinner
   └─ Create FormData with image

T0+200ms: HTTP Request
   ├─ POST /palm/analyze
   ├─ Headers: Authorization: Bearer [JWT]
   ├─ Body: multipart/form-data + image
   └─ CORS preflight check

T0+500ms: Backend Auth
   ├─ Extract JWT from Authorization header
   ├─ Decode and verify signature (SECRET_KEY)
   ├─ Validate token expiration
   ├─ Query users table for user_id
   └─ Attach User object to request

T0+700ms: Backend Image Processing
   ├─ Save image to /uploads/palms/[user_id]/[timestamp].jpg
   ├─ Load ML model from memory
   ├─ Extract palm features (MediaPipe)
   ├─ Run TensorFlow model
   └─ Get prediction scores

T0+5000ms: AI Interpretation
   ├─ Format scores into prompt
   ├─ Call Google Gemini API
   ├─ Wait for response (network latency)
   ├─ Parse JSON response
   └─ Format results

T0+5500ms: Database Write
   ├─ BEGIN TRANSACTION
   ├─ INSERT INTO palm_analyses (user_id, scores, image_path, ...)
   ├─ Get analysis_id from INSERT
   ├─ INSERT INTO palm_interpretations (analysis_id, personality_type, ...)
   ├─ COMMIT
   └─ Return results to API

T0+5600ms: HTTP Response
   ├─ 200 OK
   ├─ Content-Type: application/json
   ├─ Body: {analysis_id, scores, interpretation, ...}
   └─ Send to frontend

T0+5700ms: Frontend
   ├─ Receive response
   ├─ Hide loading spinner
   ├─ Parse response JSON
   ├─ Update React state
   ├─ Re-render UI with results
   └─ Display personality report

T0+6000ms: Complete
   └─ User sees analysis results and recommendations
```

---

## 9. Network Connectivity Requirements

### Frontend → Backend
```
Protocol: HTTPS (HTTP in dev)
Method: JSON over HTTP
Port: 443 (HTTPS) or 8000 (dev)
CORS: Must be configured on backend
Authentication: JWT Bearer token
Data Format: JSON
Max payload: Depends on nginx/backend config
Timeout: Typically 30-60 seconds
```

### Backend → PostgreSQL
```
Protocol: TCP
Port: 5432
Connection String: postgresql://...
Driver: psycopg2-binary
SSL: Required in production
Connection Pool: Default 5-10 connections
Timeout: 30 seconds
Retry Logic: SQLAlchemy handles
```

### Backend → Google Gemini API
```
Protocol: HTTPS REST API
Endpoint: https://generativelanguage.googleapis.com
Authentication: API Key
Rate Limits: Depends on API plan
Timeout: 30-60 seconds (AI response time varies)
Retry Logic: Should implement exponential backoff
```

---

## 10. Security Boundaries

```
┌─────────────────────────────────────────────────────────┐
│                    INTERNET (Public)                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Frontend (HTTPS only)                                 │
│  ├─ No sensitive data stored (except JWT token)        │
│  └─ Token in localStorage (vulnerable to XSS)         │
│                                                          │
└──────────────────┬───────────────────────────────────────┘
                   │
        HTTPS with valid TLS cert
        JSON payload only (no credentials in URL)
                   │
                   ▼
┌──────────────────────────────────────────────────────────┐
│            Application Server Boundary                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Backend (Firewalled)                                  │
│  ├─ Validates all incoming requests                    │
│  ├─ Checks JWT signature with SECRET_KEY              │
│  ├─ Verifies user authorization                       │
│  └─ Encrypts password storage                          │
│                                                          │
└──────────────────┬───────────────────────────────────────┘
                   │
        SQL connection with credentials
        psycopg2 SSL connection (production)
                   │
                   ▼
┌──────────────────────────────────────────────────────────┐
│            Database Server Boundary                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  PostgreSQL (Private network)                          │
│  ├─ Only accepts connections from backend             │
│  ├─ User passwords stored as bcrypt hashes            │
│  ├─ No direct public internet access                   │
│  └─ Automatic backups                                  │
│                                                          │
└──────────────────────────────────────────────────────────┘

Security Layers:
1. HTTPS encryption for data in transit
2. JWT signature verification for authentication
3. bcrypt password hashing for storage
4. SQL parameterization to prevent injection
5. Network isolation (database not public)
6. CORS restrictions (frontend only)
```

---

## Summary

This architecture provides:
- ✅ Clear separation of concerns (Frontend / API / Database)
- ✅ Stateless backend (scales horizontally)
- ✅ Managed database (automatic backups)
- ✅ Secure authentication (JWT + bcrypt)
- ✅ External AI integration (Google Gemini)
- ✅ Production-ready stack (FastAPI + PostgreSQL + React)

Once environment variables are properly configured in deployment, all three tiers can communicate securely and reliably.

---

**Last Updated:** August 12, 2026
