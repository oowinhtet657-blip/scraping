# 🚀 QUICKSTART: Dari Scraper ke Web App (15 Langkah)

Ikuti langkah-langkah ini untuk mengubah scraper menjadi web application.

---

## ✅ CHECKLIST

### **PHASE 1: Setup Folder & Dependencies**

- [ ] 1. **Buat struktur folder**
  ```bash
  mkdir fbscrape-webapp
  cd fbscrape-webapp
  mkdir backend frontend scraper output
  ```

- [ ] 2. **Refactor scraper.py ke module** (15 menit)
  - Copy `PostParser` class → `scraper/parser.py`
  - Copy `ExcelExporter` class → `scraper/exporter.py`
  - Copy `FBGroupScraper` class → `scraper/scraper.py`
  - Buat `scraper/__init__.py` kosong

- [ ] 3. **Setup database dengan Docker** (10 menit)
  ```bash
  # Buat docker-compose.yml
  docker-compose up -d
  
  # Test koneksi
  psql -h localhost -U scraper -d fbscraper
  ```

### **PHASE 2: Backend Setup (FastAPI)**

- [ ] 4. **Setup Python virtual environment** (5 menit)
  ```bash
  python -m venv venv
  venv\Scripts\activate  # Windows
  source venv/bin/activate  # Mac/Linux
  ```

- [ ] 5. **Install dependencies** (5 menit)
  ```bash
  pip install -r requirements-backend.txt
  ```

- [ ] 6. **Create database models** (20 menit)
  - Buat `backend/app/models/database.py`
  - Define `ScrapingJob` table dengan SQLAlchemy

- [ ] 7. **Create FastAPI app** (30 menit)
  - Setup `backend/app/main.py`
  - Buat routes di `backend/app/routes/jobs.py`
  - Buat routes di `backend/app/routes/results.py`

- [ ] 8. **Setup Celery tasks** (20 menit)
  - Buat `backend/app/tasks/scraper_task.py`
  - Config Celery dengan Redis

- [ ] 9. **Setup environment variables** (5 menit)
  - Buat `backend/.env` file
  - Add DATABASE_URL, CELERY_BROKER_URL, etc

### **PHASE 3: Frontend Setup (React)**

- [ ] 10. **Initialize React project** (10 menit)
  ```bash
  npm create vite@latest frontend -- --template react
  cd frontend
  npm install axios
  ```

- [ ] 11. **Create API service** (10 menit)
  - Buat `frontend/src/services/api.js`
  - Setup axios instance dengan BASE_URL

- [ ] 12. **Create components** (45 menit)
  - `LandingPage.jsx` - Form input
  - `JobProgress.jsx` - Progress tracking
  - Form + styling dengan TailwindCSS

- [ ] 13. **Create main App component** (15 menit)
  - Setup routing antar components
  - State management untuk job ID

### **PHASE 4: Testing & Running**

- [ ] 14. **Run semua services** (2 menit)
  ```bash
  # Terminal 1 - Backend API
  cd backend
  uvicorn app.main:app --reload
  
  # Terminal 2 - Celery Worker
  cd backend
  celery -A app.tasks.scraper_task worker --loglevel=info
  
  # Terminal 3 - Frontend
  cd frontend
  npm run dev
  ```

- [ ] 15. **Test di browser** (10 menit)
  - Buka http://localhost:3000
  - Masukkan Facebook group URL
  - Monitor progress
  - Download hasil Excel

---

## ⏱️ Estimasi Waktu Total

| Phase | Waktu |
|-------|-------|
| Setup Folder & Dependencies | 30 menit |
| Backend Setup | 2 jam |
| Frontend Setup | 1.5 jam |
| Testing & Debugging | 1 jam |
| **TOTAL** | **5 jam** |

---

## 📋 Pre-requisites

```bash
# Cek versi
python --version  # >= 3.9
node --version    # >= 16
docker --version  # Latest

# Install jika belum
# Python: https://www.python.org/
# Node: https://nodejs.org/
# Docker: https://www.docker.com/
```

---

## 🔧 Troubleshooting Cepat

| Masalah | Solusi |
|---------|--------|
| `ModuleNotFoundError: No module named 'fastapi'` | `pip install -r requirements-backend.txt` |
| `Connection refused` (Database) | `docker-compose up -d` |
| `Port 3000 sudah terpakai` | `npm run dev -- --port 3001` |
| `CORS error` | Cek `app.add_middleware(CORSMiddleware, ...)` |
| Celery task timeout | Naikkan `CELERY_TASK_TIME_LIMIT = 7200` |

---

## 📁 File Priority (Mulai dari sini)

**Wajib dibuat DULUAN (dalam urutan):**

1. ✅ `scraper/` folder stucture (refactor from main scraper.py)
2. ✅ `backend/.env` (database credentials)
3. ✅ `backend/app/models/database.py` (database schema)
4. ✅ `backend/app/main.py` (FastAPI app)
5. ✅ `backend/app/routes/jobs.py` (job endpoints)
6. ✅ `frontend/src/services/api.js` (API client)
7. ✅ `frontend/src/components/LandingPage.jsx` (main form)

**Opsional tapi recommended:**

- `backend/app/routes/results.py` (download file)
- `frontend/src/components/JobProgress.jsx` (progress bar)
- Error handling & logging
- Tests

---

## 🎯 Minimal Viable Product (MVP)

Untuk MVP pertama, MINIMAL features:

```python
# Backend endpoints yang WAJIB:
POST /api/jobs/start → start scraping
GET /api/jobs/status/{id} → get progress
GET /api/results/download/{id} → download Excel

# Frontend screens yang WAJIB:
1. Landing page dengan form
2. Progress page dengan live updates
3. Download button
```

**Dengan ini saja sudah FUNCTIONAL! ✨**

---

## 💡 Tips & Best Practice

1. **Jangan buat semuanya sekaligus** - Mulai dari backend dulu, test dengan Postman
2. **Use Postman/Thunder Client** - Test API sebelum integrate ke frontend
3. **Logger everywhere** - Print logs untuk debug, jangan hanya errors
4. **Database backup** - Backup database sebelum production
5. **Keep credentials secure** - Jangan push `.env` ke GitHub

---

## 🚀 Deploy Checklist (Setelah MVP selesai)

- [ ] Setup CI/CD (GitHub Actions)
- [ ] Add authentication (JWT)
- [ ] Setup monitoring (Sentry, DataDog)
- [ ] Database backup strategy
- [ ] SSL certificate (HTTPS)
- [ ] Rate limiting
- [ ] Logging & analytics

---

**Butuh bantuan? Refer ke README_WEBAPP.md untuk detail lengkap!**

Happy coding! 🎉
