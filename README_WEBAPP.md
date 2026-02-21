# 🚀 Panduan Lengkap: Scraping Tool Menjadi Web Application

Dokumentasi ini menjelaskan **step-by-step** cara mengubah scraper.py menjadi **web application full-stack** dengan Frontend, Backend, dan Database.

---

## 📋 Daftar Isi
1. [Arsitektur Aplikasi](#arsitektur-aplikasi)
2. [Tech Stack yang Direkomendasikan](#tech-stack-yang-direkomendasikan)
3. [Struktur Folder](#struktur-folder)
4. [Step-by-Step Implementation](#step-by-step-implementation)
5. [Deployment](#deployment)

---

## 🏗️ Arsitektur Aplikasi

```
┌─────────────────────────────────────────────────────┐
│             FRONTEND (React/Vue)                     │
│  - Landing Page                                     │
│  - Input Form (Link, Max Posts, Settings)          │
│  - Job Progress Monitor                             │
│  - Download Results                                 │
└────────────────┬────────────────────────────────────┘
                 │
                 │ HTTP/REST API
                 ↓
┌─────────────────────────────────────────────────────┐
│           BACKEND (FastAPI/Flask)                    │
│  - REST API Endpoints                               │
│  - Job Queue (Celery)                               │
│  - Validator Input                                  │
│  - Database Management                              │
│  - File Storage Handler                             │
└────────────────┬────────────────────────────────────┘
                 │
      ┌──────────┼──────────┐
      ↓          ↓          ↓
   DATABASE   REDIS      FILE STORAGE
  (PostgreSQL) (Queue)   (Local/AWS S3)
```

---

## 🛠️ Tech Stack yang Direkomendasikan

### **FRONTEND:**
- **React** (Modern, Component-based)
- **Vite** (Fast build tool)
- **TailwindCSS** (Styling)
- **Axios** (HTTP Client)

**Alternatif:** Vue 3 + Vite (lebih ringan)

### **BACKEND:**
- **FastAPI** (Fast, async, modern Python)
- **Celery** (Async task queue untuk scraping)
- **PostgreSQL** (Database relasional)
- **SQLAlchemy** (ORM)
- **Redis** (Message broker untuk Celery)

**Alternatif:** Flask + Gunicorn (lebih simple)

### **STORAGE:**
- **Local File System** (Development)
- **AWS S3** (Production)
- **MinIO** (Self-hosted alternative untuk S3)

---

## 📁 Struktur Folder yang Direkomendasikan

```
fbscrape-webapp/
├── frontend/                      # React App
│   ├── src/
│   │   ├── components/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── ConfigForm.jsx
│   │   │   ├── JobProgress.jsx
│   │   │   └── ResultsDownload.jsx
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.js            # Axios instance
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                       # FastAPI App
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── models/
│   │   │   └── database.py       # SQLAlchemy models
│   │   ├── schemas/
│   │   │   └── scrape_job.py    # Pydantic schemas
│   │   ├── routes/
│   │   │   ├── jobs.py          # Job endpoints
│   │   │   ├── results.py       # Results endpoints
│   │   │   └── health.py        # Health check
│   │   ├── tasks/
│   │   │   └── scraper_task.py  # Celery tasks
│   │   ├── services/
│   │   │   ├── scraper_service.py  # Scraping logic
│   │   │   └── storage_service.py   # File handling
│   │   ├── config.py            # Configuration
│   │   └── core/
│   │       └── security.py      # Auth (optional)
│   ├── requirements.txt
│   ├── celery_worker.py         # Celery worker config
│   └── docker-compose.yml
│
├── scraper/                       # Original scraper.py (refactored)
│   ├── __init__.py
│   ├── parser.py                # PostParser class
│   ├── scraper.py               # FBGroupScraper class
│   └── exporter.py              # ExcelExporter class
│
├── .env                          # Environment variables
├── .gitignore
├── docker-compose.yml            # Docker containerization
└── README.md
```

---

## 📝 Step-by-Step Implementation

### **STEP 1: Refactor scraper.py Menjadi Module**

**Tujuan:** Pisahkan scraper logic supaya bisa di-reuse di backend

#### 1.1 Buat `scraper/parser.py`:
```python
# Pindahkan class PostParser ke sini
class PostParser:
    @staticmethod
    def parse(text: str) -> dict:
        # ... existing code
```

#### 1.2 Buat `scraper/exporter.py`:
```python
# Pindahkan class ExcelExporter ke sini
class ExcelExporter:
    @classmethod
    def export(cls, posts: list[dict], filepath: str):
        # ... existing code
```

#### 1.3 Buat `scraper/scraper.py`:
```python
# Pindahkan class FBGroupScraper ke sini
# Modifikasi untuk bisa dipanggil dari task celery

class FBGroupScraper:
    def __init__(self, config: dict):
        # ... modified untuk support async callback
    
    async def run(self, progress_callback=None):
        # ... add progress_callback untuk update UI
```

---

### **STEP 2: Setup Backend dengan FastAPI**

#### 2.1 Install dependencies:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary celery redis
```

#### 2.2 Buat `backend/app/main.py`:
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes import jobs, results

app = FastAPI(
    title="FB Scraper API",
    version="1.0.0",
    description="Facebook Group Scraper Web Service"
)

# CORS untuk frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(results.router, prefix="/api/results", tags=["results"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

#### 2.3 Buat `backend/app/models/database.py`:
```python
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)  # Celery task ID
    group_url = Column(String)
    max_posts = Column(Integer)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100%
    result_file = Column(String, nullable=True)  # Path ke file Excel
    error_message = Column(String, nullable=True)
    config = Column(JSON)  # Store full config
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_posts = Column(Integer, default=0)
    total_wa = Column(Integer, default=0)
```

#### 2.4 Buat `backend/app/routes/jobs.py`:
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from celery import current_app
from app.tasks.scraper_task import start_scraping_task
from app.models.database import ScrapingJob
from sqlalchemy.orm import Session

router = APIRouter()

class JobConfig(BaseModel):
    group_url: str
    max_posts: int = 400
    scroll_pause_min: float = 4.0
    scroll_pause_max: float = 6.0

@router.post("/start")
async def start_job(config: JobConfig, db: Session):
    """Start scraping job"""
    
    # Validate URL
    if "facebook.com/groups/" not in config.group_url:
        raise HTTPException(status_code=400, detail="Invalid Facebook group URL")
    
    # Create job record
    job = ScrapingJob(
        group_url=config.group_url,
        max_posts=config.max_posts,
        config=config.dict()
    )
    db.add(job)
    db.commit()
    
    # Send to Celery
    task = start_scraping_task.delay(job.id, config.dict())
    job.job_id = task.id
    db.commit()
    
    return {
        "job_id": job.id,
        "task_id": task.id,
        "status": "pending"
    }

@router.get("/status/{job_id}")
async def get_job_status(job_id: int, db: Session):
    """Get job status & progress"""
    
    job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": job.id,
        "status": job.status,
        "progress": job.progress,
        "total_posts": job.total_posts,
        "total_wa": job.total_wa,
        "completed_at": job.completed_at,
        "error": job.error_message
    }

@router.get("/list")
async def list_jobs(db: Session, limit: int = 20):
    """List recent jobs"""
    
    jobs = db.query(ScrapingJob)\
        .order_by(ScrapingJob.created_at.desc())\
        .limit(limit)\
        .all()
    
    return [
        {
            "id": j.id,
            "url": j.group_url,
            "status": j.status,
            "created_at": j.created_at,
            "completed_at": j.completed_at
        }
        for j in jobs
    ]
```

#### 2.5 Buat `backend/app/routes/results.py`:
```python
from fastapi import APIRouter, HTTPException, FileResponse
from app.models.database import ScrapingJob
from sqlalchemy.orm import Session
import os

router = APIRouter()

@router.get("/download/{job_id}")
async def download_result(job_id: int, db: Session):
    """Download Excel file hasil scraping"""
    
    job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
    if not job or not job.result_file:
        raise HTTPException(status_code=404, detail="Result not found")
    
    if not os.path.exists(job.result_file):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        job.result_file,
        filename=os.path.basename(job.result_file),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/{job_id}")
async def get_result_info(job_id: int, db: Session):
    """Get result info"""
    
    job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": job.id,
        "total_posts": job.total_posts,
        "total_wa": job.total_wa,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "file": job.result_file
    }
```

#### 2.6 Buat `backend/app/tasks/scraper_task.py`:
```python
from celery import shared_task, current_task
from app.models.database import ScrapingJob, JobStatus
from sqlalchemy.orm import Session
import asyncio
from scraper.scraper import FBGroupScraper

@shared_task(bind=True)
def start_scraping_task(self, job_id: int, config: dict):
    """Celery task untuk scraping"""
    
    db = Session()
    job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
    
    if not job:
        return {"error": "Job not found"}
    
    try:
        job.status = JobStatus.RUNNING
        db.commit()
        
        # Run scraper asynchronously
        scraper = FBGroupScraper(config)
        
        # Custom progress callback
        def update_progress(current, total, wa_count):
            job.progress = int((current / total) * 100)
            job.total_posts = current
            job.total_wa = wa_count
            db.commit()
            
            # Update Celery task state
            current_task.update_state(
                state='PROGRESS',
                meta={'progress': job.progress, 'total': total}
            )
        
        # Run scraper
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        posts = loop.run_until_complete(scraper.run())
        loop.close()
        
        # Save to Excel
        from datetime import datetime
        filename = f"output/result_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        from scraper.exporter import ExcelExporter
        ExcelExporter.export(posts, filename)
        
        job.status = JobStatus.COMPLETED
        job.result_file = filename
        job.total_posts = len(posts)
        job.total_wa = sum(1 for p in posts if p.get('nomor_wa'))
        job.completed_at = datetime.utcnow()
        db.commit()
        
        return {"status": "completed", "posts": len(posts), "file": filename}
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        db.commit()
        return {"error": str(e)}
    finally:
        db.close()
```

---

### **STEP 3: Setup Frontend dengan React + Vite**

#### 3.1 Create React app:
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install axios
npm install -D tailwindcss postcss autoprefixer
```

#### 3.2 Buat `frontend/src/services/api.js`:
```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const jobService = {
  startJob: (config) => api.post('/jobs/start', config),
  getStatus: (jobId) => api.get(`/jobs/status/${jobId}`),
  listJobs: (limit = 20) => api.get(`/jobs/list?limit=${limit}`),
};

export const resultService = {
  downloadResult: (jobId) => 
    api.get(`/results/download/${jobId}`, { responseType: 'blob' }),
  getResultInfo: (jobId) => api.get(`/results/${jobId}`),
};

export default api;
```

#### 3.3 Buat `frontend/src/components/LandingPage.jsx`:
```jsx
import React, { useState } from 'react';
import { jobService } from '../services/api';

export default function LandingPage({ onJobStart }) {
  const [formData, setFormData] = useState({
    group_url: '',
    max_posts: 400,
    scroll_pause_min: 4.0,
    scroll_pause_max: 6.0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name.includes('max') ? parseInt(value) : parseFloat(value) || value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await jobService.startJob(formData);
      onJobStart(response.data.job_id, response.data.task_id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error starting job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">FB Scraper</h1>
        <p className="text-gray-600 mb-6">Scrape Facebook Group Posts & Phone Numbers</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Facebook Group URL
            </label>
            <input
              type="url"
              name="group_url"
              value={formData.group_url}
              onChange={handleChange}
              placeholder="https://www.facebook.com/groups/..."
              required
              className="mt-1 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Max Posts: {formData.max_posts}
            </label>
            <input
              type="range"
              name="max_posts"
              min="10"
              max="1000"
              value={formData.max_posts}
              onChange={handleChange}
              className="w-full"
            />
          </div>

          {error && (
            <div className="bg-red-100 text-red-700 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded-lg transition duration-200"
          >
            {loading ? 'Starting...' : 'Start Scraping'}
          </button>
        </form>
      </div>
    </div>
  );
}
```

#### 3.4 Buat `frontend/src/components/JobProgress.jsx`:
```jsx
import React, { useEffect, useState } from 'react';
import { jobService, resultService } from '../services/api';

export default function JobProgress({ jobId, taskId, onComplete }) {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await jobService.getStatus(jobId);
        setJob(response.data);

        if (response.data.status === 'completed' || response.data.status === 'failed') {
          clearInterval(interval);
          onComplete?.(response.data);
        }
      } catch (err) {
        console.error('Error fetching status:', err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  if (!job) return <div>Loading...</div>;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">Scraping Progress</h2>
      
      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-600">Status</p>
          <p className="text-lg font-semibold">{job.status.toUpperCase()}</p>
        </div>

        <div>
          <p className="text-sm text-gray-600">Progress</p>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div 
              className="bg-blue-600 h-4 rounded-full transition-all"
              style={{ width: `${job.progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-1">{job.progress}%</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Total Posts</p>
            <p className="text-xl font-bold">{job.total_posts}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Phone Numbers</p>
            <p className="text-xl font-bold text-green-600">{job.total_wa}</p>
          </div>
        </div>

        {job.status === 'completed' && (
          <button
            onClick={() => resultService.downloadResult(jobId)}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg"
          >
            📥 Download Excel
          </button>
        )}

        {job.error && (
          <div className="bg-red-100 text-red-700 p-3 rounded-lg">
            Error: {job.error}
          </div>
        )}
      </div>
    </div>
  );
}
```

---

### **STEP 4: Database & Docker Setup**

#### 4.1 Buat `docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: scraper
      POSTGRES_PASSWORD: scraper123
      POSTGRES_DB: fbscraper
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### 4.2 Jalankan:
```bash
docker-compose up -d
```

---

### **STEP 5: Environment Configuration**

Buat `backend/.env`:
```
# Database
DATABASE_URL=postgresql://scraper:scraper123@localhost:5432/fbscraper

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Storage
STORAGE_PATH=./output
MAX_FILE_SIZE=104857600  # 100MB

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Chrome
CHROME_EXECUTABLE=C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe
CHROME_USER_DATA=/path/to/chrome/profile
```

---

### **STEP 6: Run Everything**

#### Terminal 1 - Backend API:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Celery Worker:
```bash
cd backend
celery -A app.tasks.scraper_task worker --loglevel=info
```

#### Terminal 3 - Frontend:
```bash
cd frontend
npm run dev
```

Akses di: **http://localhost:3000** ✨

---

## 🚀 Deployment

### **Option 1: Docker + AWS EC2**

#### Buat `Dockerfile` backend:
```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build & Push:
```bash
docker build -t fbscraper-backend .
docker tag fbscraper-backend:latest yourusername/fbscraper-backend:latest
docker push yourusername/fbscraper-backend:latest
```

### **Option 2: Vercel (Frontend) + Railway (Backend)**

**Frontend ke Vercel:**
```bash
npm install -g vercel
vercel
```

**Backend ke Railway:**
- Connect GitHub repo
- Select Python
- Add PostgreSQL & Redis databases
- Deploy!

---

## 📊 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs/start` | Start scraping job |
| GET | `/api/jobs/status/{id}` | Get job status |
| GET | `/api/jobs/list` | List all jobs |
| GET | `/api/results/{id}` | Get result info |
| GET | `/api/results/download/{id}` | Download Excel file |
| GET | `/health` | Health check |

---

## 🔒 Security Tips

1. **Input Validation** - Validasi URL Facebook
2. **Rate Limiting** - Batasi requests per IP
3. **Authentication** - Add API keys/JWT untuk public access
4. **CORS** - Restrict origins yang diizinkan
5. **File Upload Limits** - Max file size 100MB
6. **Error Handling** - Jangan expose server errors

---

## 📚 Referensi Useful

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Celery Docs**: https://docs.celeryproject.org/
- **React Docs**: https://react.dev/
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org/

---

## ❓ FAQ

**Q: Bisakah di-host di server biasa (non-Docker)?**
A: Ya! Hanya perlu install Python, PostgreSQL, Redis, dan npm. Skip langkah Docker.

**Q: Berapa biaya hosting?**
A: 
- Railway + Vercel: ~$10/bulan (free tier available)
- AWS: Mulai dari $5/bulan untuk micro instance

**Q: Berapa traffic yg bisa ditangani?**
A: Dengan setup di atas, bisa handle ~100 concurrent jobs dengan baik.

**Q: Bagaimana cara backup database?**
A: `pg_dump fbscraper > backup.sql`

---

## 🎯 Next Phase (Advanced)

1. **Authentication** - Add user login system
2. **Analytics** - Dashboard untuk stats scraping
3. **Scheduler** - Auto-scrape tertentu waktu
4. **Notifications** - Email/Telegram saat selesai
5. **Admin Panel** - Manage jobs & users

---

**Happy Coding! 🚀**
