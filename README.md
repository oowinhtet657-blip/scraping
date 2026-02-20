# FB Group Scraper — Playwright + Chrome Remote Debug

Scraper Facebook Group dengan Python menggunakan Playwright + Chrome Remote Debug Port. Script konek langsung ke Chrome yang sudah login (tidak perlu password di script).

## Struktur Project
```
FBscrap/
├── scraper.py           ← Script utama
├── requirements.txt     ← Dependensi Python
├── chrome.bat           ← Helper: buka Chrome dengan debug port
├── README.md            ← File ini
└── output/              ← Hasil scraping (auto-dibuat)
    ├── posts_YYYYMMDD_HHMMSS.json
    └── posts_YYYYMMDD_HHMMSS.xlsx
```

---

## 🚀 Setup (Sekali Saja)

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

atau manual:
```powershell
pip install playwright openpyxl requests
```

### 2. Cek Chrome Terinstall

Script otomatis deteksi Chrome di:
- Windows: `C:\Program Files\Google\Chrome\Application\chrome.exe`

Jika Chrome di lokasi berbeda, edit line 90 di `scraper.py`:
```python
"chrome_executable": r"C:\Path\To\Your\chrome.exe",
```

---

## ⚙️ Konfigurasi

Edit bagian `CONFIG` di **scraper.py** (line 87-102):

```python
CONFIG = {
    # Chrome User Data — HARUS sesuai username Windows Anda
    "chrome_user_data_dir": r"C:\Users\{USERNAME}\AppData\Local\Google\Chrome\User Data",
    "chrome_profile":       "Default",
    "chrome_executable":    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    
    # Remote Debug Port (jangan diubah kecuali ada konflik)
    "debug_port":           9222,
    
    # Target Group & Scraping Settings
    "group_url":    "https://www.facebook.com/groups/203507351093781",  # ← Ganti URL grup
    "max_posts":    100,
    "scroll_pause": (2.5, 4.5),
}
```

**⚠️ PENTING:**
- Ganti `{USERNAME}` dengan username Windows Anda (cek dari `C:\Users\`)
- Ganti `group_url` dengan URL grup Facebook target

---

## ✅ Persiapan Awal

### 1. Login ke Facebook
```powershell
# Buka Chrome secara normal
# Login ke Facebook dengan akun yang ingin digunakan
# **Pastikan tetap login, jangan logout**
# Chrome bisa tetap terbuka atau ditutup
```

### 2. Verifikasi Setup
```powershell
# Cek username Windows Anda
whoami
```

Sesuaikan `chrome_user_data_dir` di CONFIG dengan username yang muncul.

---

## 🎯 Menjalankan Script

### Opsi A: Chrome Belum Terbuka
```powershell
python scraper.py
```

Script akan:
1. ✅ Detect Chrome belum running
2. ✅ Buka Chrome otomatis dengan debug port
3. ✅ Tunggu halaman group loading
4. ✅ Mulai scraping

### Opsi B: Chrome Sudah Terbuka
```powershell
python scraper.py
```

Script akan:
1. ✅ Detect Chrome sudah running
2. ✅ Konek langsung (tidak perlu restart Chrome)
3. ✅ Mulai scraping tanpa gangguan

---

## 📊 Output

Hasil scraping tersimpan di folder `output/`:

- **posts_YYYYMMDD_HHMMSS.json** — Data raw (JSON)
- **posts_YYYYMMDD_HHMMSS.xlsx** — Excel dengan format rapi

---

## 🐛 Troubleshooting

### Error: "Chrome tidak ditemukan di..."
→ Edit `chrome_executable` di CONFIG dengan path yang benar

### Error: "Chrome tidak merespons di port 9222"
→ Pastikan Chrome sudah login ke Facebook sebelum menjalankan script

### Chrome tiba-tiba close saat scraping
→ Jangan close Chrome manual. Biarin script handle, atau tambah jeda waktu scroll

### Hasil scraping kosong
→ Cek apakah URL grup benar dan akun bisa akses grup tersebut

---

## 💡 Tips

1. **Jangan set max_posts terlalu besar** — maks 200-300 per sesi
2. **Scroll pause** — biarin jeda natural (2.5-4.5 detik), jangan kurangi
3. **Buka di jam normal** — jangan scrape 24/7 untuk hindari suspicious activity
4. **Jika ada CAPTCHA** — selesaikan manual di browser (Chrome tetap terbuka)
5. Pakai VPN/proxy residensial kalau IP sudah di-flag

## Troubleshooting

| Masalah | Solusi |
|---|---|
| Login gagal | Cek email/password, atau FB minta verifikasi 2FA |
| 0 postingan ditemukan | Facebook ganti selector — perlu update CSS selector di `_extract_posts()` |
| Script lambat | Normal, jeda sengaja dipasang untuk hindari deteksi |
| Kena CAPTCHA | Set headless=False, selesaikan manual, lanjut otomatis |

## Update Selector

Facebook sering ganti class HTML. Kalau tiba-tiba 0 postingan:

1. Buka grup di Chrome
2. Klik kanan teks postingan → Inspect
3. Cari class/attribute unik dari container teks
4. Update list `selectors` di method `_extract_posts()`
