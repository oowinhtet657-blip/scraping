# 🚀 Facebook Group Scraper - Web Landing Page

**Landing page sederhana untuk mengoperasikan `scraper.py` dari browser.**

---

## Cara Kerja

1. **Input form** → URL grup Facebook, target jumlah posts, Chrome debug port
2. **Submit** → Backend jalankan scraper (import `FBGroupScraper` dari scraper.py)
3. **Hasil** → Tampil di tabel + statistik
4. **Download** → Export ke JSON atau Excel

---

## Setup & Run

### 1️⃣ Install Dependencies
```powershell
cd C:\Users\KuroX66\FBscrap
pip install -r requirements-app.txt
```

### 2️⃣ Buka Chrome dengan Debug Port
```powershell
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\KuroX66\AppData\Local\Google\Chrome\User Data" https://www.facebook.com
```
- Chrome harus **sudah login** ke akun Facebook
- Biarkan terbuka selama scraping berjalan

### 3️⃣ Jalankan Flask App
```powershell
cd C:\Users\KuroX66\FBscrap
python app.py
```

Output:
```
============================================================
🚀 Facebook Group Scraper Web App
============================================================
Akses: http://localhost:5000
============================================================
```

### 4️⃣ Buka di Browser
```
http://localhost:5000
```

---

## Fitur

✅ **Input Form**
- URL Facebook Group
- Max posts (1-500)
- Chrome debug port (default 9222)

✅ **Progress & Status**
- Loading indicator saat scraping
- Error message jika ada masalah
- Success message + total posts

✅ **Results Display**
- Statistik: Total posts, dengan WA, dengan harga, rata-rata harga
- Tabel hasil dengan columns: barang, harga, BH%, garansi, nomor WA, TT/BT
- Scrollable & responsive

✅ **Download**
- Export ke Excel (.xlsx)
- Export ke JSON

---

## Struktur File

```
C:\Users\KuroX66\FBscrap\
├── app.py                    # Flask app utama
├── scraper.py               # Original scraper (yang di-import)
├── requirements-app.txt     # Dependencies Flask
├── templates/
│   └── index.html          # Landing page UI
└── output/                 # Folder hasil scraping (auto-created)
```

---

## Troubleshooting

### ❌ "Chrome tidak merespons di port 9222"
- Pastikan Chrome sudah dibuka dengan `--remote-debugging-port=9222`
- Buka `http://localhost:9222/json` di browser untuk cek

### ❌ "Facebook belum login"
- Buka Chrome secara normal, login ke Facebook
- Jalankan scraper lagi

### ❌ "Port 5000 already in use"
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

---

## Catatan

- **Jangan tutup Chrome** selama scraping berjalan
- Scraping bisa memakan waktu tergantung jumlah posts
- Results disimpan di folder `output/`
- Aplikasi non-blocking, tapi scraping tetap async

---

## Code Structure

**app.py** - Flask:
- `GET /` → Serve landing page
- `POST /api/scrape` → Jalankan scraper
- `POST /api/download/<format>` → Download hasil
- `GET /api/health` → Health check

**templates/index.html** - UI:
- Input form
- Results table + stats
- Download buttons
- Real-time validation

---

Selesai! Tinggal buka browser & mulai scraping! 🎉
