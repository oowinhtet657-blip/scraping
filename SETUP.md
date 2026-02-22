# 🚀 SETUP GUIDE: Menjalankan FB Scraper WebApp

## 📋 Prerequisites

Pastikan sudah terinstall:
- **Python 3.8+**
- **Node.js 16+** (untuk frontend)
- **Chrome Browser** (untuk scraping)

## 🔧 Setup Backend

### 1. Navigasi ke folder backend
```bash
cd backend
```

### 2. Buat virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements-backend.txt
```

### 4. Setup environment variables
- Copy `.env` file yang sudah ada di backend folder
- Edit sesuai kebutuhan Anda (optional)

### 5. Run FastAPI server
```bash
# Development (dengan auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server akan berjalan di: **http://localhost:8000**
API Docs tersedia di: **http://localhost:8000/docs**

---

## 🎨 Setup Frontend

### 1. Navigasi ke folder frontend
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Setup environment variables
- Edit file `.env` di folder frontend
- Pastikan `VITE_API_URL=http://localhost:8000/api`

### 4. Run development server
```bash
npm run dev
```

Server akan berjalan di: **http://localhost:5173** (atau port lain jika 5173 sudah terpakai)

Browser akan terbuka otomatis.

---

## 🚀 Menjalankan Aplikasi Lengkap

### Terminal 1 - Backend API
```bash
cd backend
source venv/bin/activate  # atau venv\Scripts\activate di Windows
uvicorn app.main:app --reload
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

### Terminal 3 (Optional) - Chrome dengan Debug Port
Jika Chrome belum terbuka dengan debug port, buka terminal baru:

**Windows:**
```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\{YOUR_USERNAME}\AppData\Local\Google\Chrome\User Data"
```

**Mac:**
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222
```

**Linux:**
```bash
google-chrome --remote-debugging-port=9222
```

---

## ✅ Testing

### Test Backend API
```bash
# Health check
curl http://localhost:8000/health

# List jobs
curl http://localhost:8000/api/jobs/
```

### Test Frontend
Buka browser dan navigasi ke **http://localhost:5173**

---

## 🔗 API Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/health` | GET | Health check |
| `/api/jobs/` | GET | List semua jobs |
| `/api/jobs/create` | POST | Create scraping job |
| `/api/jobs/{job_id}` | GET | Get job details |
| `/api/jobs/{job_id}/start` | POST | Start scraping |
| `/api/jobs/{job_id}/results` | GET | Get results |
| `/api/jobs/{job_id}` | DELETE | Delete job |

---

## 📁 Folder Structure

```
FBscrap/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── main.py       # FastAPI app
│   │   ├── models/       # Database models
│   │   ├── routes/       # API routes
│   │   └── schemas/      # Pydantic schemas
│   ├── requirements-backend.txt
│   └── .env
│
├── frontend/             # React Frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API service
│   │   ├── App.jsx       # Main app
│   │   └── main.jsx      # Entry point
│   ├── package.json
│   └── .env
│
├── scraper/              # Scraper modules
│   ├── parser.py         # Text parser
│   ├── exporter.py       # Excel exporter
│   └── scraper.py        # Main scraper
│
└── output/               # Hasil scraping
```

---

## 🐛 Troubleshooting

### Port sudah terpakai
```bash
# Find process using port 8000 (backend)
lsof -i :8000

# Find process using port 5173 (frontend)
lsof -i :5173

# Kill process
kill -9 <PID>
```

### Chrome connection failed
1. Pastikan Chrome sudah login ke Facebook
2. Jalankan Chrome dengan debug port (lihat Terminal 3 di atas)
3. Verify: buka http://localhost:9222/json di browser

### CORS Error
Pastikan backend sudah menjalankan localhost dengan CORS enabled (cek di `app/main.py`)

### Import errors di Python
Pastikan virtual environment ter-activate:
```bash
which python  # Harus menunjuk ke venv
```

---

## 📝 Notes

- Database default menggunakan SQLite (untuk development)
- Untuk production, gunakan PostgreSQL
- Celery optional, hanya jika ingin async jobs
- Saat deploy, update `FRONTEND_URL` di backend `.env`

Selamat! 🎉 Webapp Anda sudah siap!
