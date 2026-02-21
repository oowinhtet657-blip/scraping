# 📱 Dokumentasi Lengkap: Logika Ekstraksi Nomor HP/WA

Dokumen ini menjelaskan **semua logika untuk mengambil nomor HP/WA** dari postingan Facebook yang disimpan di Excel/JSON.

---

## 🎯 Fungsi Utama: `_extract_wa(text)`

Lokasi: [scraper.py](scraper.py#L167-L185)

### Cara Kerja (3 Pattern Sequential):

```python
def _extract_wa(text):
    # Pattern 1: Dengan prefix + support kurung/dash
    # Pattern 2: Langsung nomor tanpa prefix
    # Pattern 3: Nomor dengan kurung/dash (fallback)
```

---

## 📋 Pattern 1: Dengan Prefix (Priority Tertinggi)

### Regex:
```regex
(?:wa|whatsapp|hub|minat|kontak)\s*[:\-]?\s*((?:08|62|\+62)[\d\s\-()]{8,14})
```

### Deteksi Format:
- ✅ `wa: 0812-3456-7890`
- ✅ `wa: 0812 3456 7890`
- ✅ `wa: (0812) 3456-7890`
- ✅ `wa: 0812 (3456) 7890`
- ✅ `wa: 0812 [3456] 7890`
- ✅ `whatsapp: 0812345678`
- ✅ `hub: 62812345678`
- ✅ `minat: +62 812 345 678`
- ✅ `kontak: +62-812-345-678`

### Penjelasan Pattern:
- `(?:wa|whatsapp|hub|minat|kontak)` → Cari kata kunci (case-insensitive)
- `\s*[:\-]?\s*` → Optional spasi, colon/dash, spasi
- `((?:08|62|\+62)[\d\s\-()]{8,14})` → Capture nomor dengan format:
  - Mulai dengan `08`, `62`, atau `+62`
  - Diikuti 8-14 karakter (bisa angka, spasi, dash, kurung)

---

## 📋 Pattern 2: Langsung Nomor (Fallback 1)

### Regex:
```regex
((?:08|62|\+62)[\d]{9,13})
```

### Deteksi Format:
- ✅ `0812345678` (tanpa spasi/dash)
- ✅ `62812345678`
- ✅ `+62812345678`

### Notes:
- **Hanya angka** — tidak support kurung/dash
- Cari jika Pattern 1 tidak ketemu

---

## 📋 Pattern 3: Nomor dengan Kurung (Fallback 2)

### Regex:
```regex
((?:08|62|\+62)[\d\s\-()]{9,14})
```

### Deteksi Format:
- ✅ `(0812) 3456 7890` (tanpa prefix)
- ✅ `0812 (3456) 7890`
- ✅ `0812 [3456] 7890`

### Notes:
- **Fallback terakhir** — cari nomor dengan format apapun
- Support kurung () dan bracket []

---

## 🧹 Cleaning/Sanitization

### Regex:
```regex
[\s\-()\[\]]
```

### Yang dihapus:
- ❌ Spasi: ` `
- ❌ Dash: `-`
- ❌ Kurung biasa: `(`, `)`
- ❌ Square bracket: `[`, `]`

### Yang tetap:
- ✅ Angka: `0-9`
- ✅ Plus: `+`

### Contoh:
```
Input:  "wa: (0812) 3456-7890"
        ↓ Extract Pattern 1 → "(0812) 3456-7890"
        ↓ Clean
Output: "08123456789O"
```

---

## 📊 Testing Examples

### Test Case 1: Format Normal
```
Input:  "wa: 0812-3456-7890"
Output: "08123456789O"  ✅
```

### Test Case 2: Format Dengan Kurung
```
Input:  "wa: (0812) 3456-7890"
Output: "08123456789O"  ✅
```

### Test Case 3: International Format
```
Input:  "WA: +62 812 345 678"
Output: "+62812345678"  ✅
```

### Test Case 4: Tanpa Prefix
```
Input:  "Hubungi langsung: 0812345678"
        (Pattern 1 tidak match)
        ↓ Pattern 2
Output: "0812345678"  ✅
```

### Test Case 5: Bracket Format
```
Input:  "No WA: [0812] 345 678"
Output: "0812345678"  ✅
```

### Test Case 6: Tidak Ada Nomor
```
Input:  "Barang ready stock"
Output: ""  (empty string)
```

---

## 🔧 Struktur di Excel

### Column: "No. WA"
- **Tipe**: String
- **Format**: `08123456789O` atau `+62812345678O`
- **Kosong**: Jika tidak ditemukan nomor

### Contoh Data Excel:
```
Row 1 (Header): No. WA
Row 2:          08123456789O
Row 3:          +6281234567
Row 4:          (kosong)
Row 5:          08198765432
```

---

## 📝 Struktur di JSON

### Field: `"nomor_wa"`
```json
{
  "barang": "iPhone 12 64GB",
  "harga": "8500000",
  "nomor_wa": "08123456789O",
  "teks_asli": "..."
}
```

---

## ⚙️ Implementasi di Kode

### Lokasi Parsing:
```python
class PostParser:
    @staticmethod
    def parse(text: str) -> dict:
        result = {
            "barang":           PostParser._extract_barang(text),
            "harga":            PostParser._extract_harga(text),
            "kondisi_baterai":  PostParser._extract_bh(text),
            "garansi":          PostParser._extract_garansi(text),
            "nomor_wa":         PostParser._extract_wa(text),  # ← di sini
            "kartu":            PostParser._extract_kartu(text),
            "kelengkapan":      PostParser._extract_kelengkapan(text),
            "tt_bt":            PostParser._extract_ttbt(text),
            "teks_asli":        text.strip(),
        }
        return result
```

### Lokasi Fungsi:
[scraper.py - Line 167-185](scraper.py#L167-L185)

```python
@staticmethod
def _extract_wa(text):
    # Pattern 1: Dengan prefix (wa, whatsapp, hub, minat, kontak)
    m = re.search(
        r"(?:wa|whatsapp|hub|minat|kontak)\s*[:\-]?\s*((?:08|62|\+62)[\d\s\-()]{8,14})",
        text, re.IGNORECASE
    )
    # Pattern 2: Langsung nomor
    if not m:
        m = re.search(r"((?:08|62|\+62)[\d]{9,13})", text)
    # Pattern 3: Nomor dengan kurung/dash (fallback)
    if not m:
        m = re.search(r"((?:08|62|\+62)[\d\s\-()]{9,14})", text)
    
    if m:
        # Clean: hapus semua spaces, dashes, kurung
        return re.sub(r"[\s\-()\[\]]", "", m.group(1))
    return ""
```

---

## 🎯 Format Nomor yang Didukung

### Prefiks Standar:
```
wa:
wa :
wa-
wa-:
whatsapp:
whatsapp:
hub:
minat:
kontak:
```

### Contoh Format Lengkap:
```
Contoh 1:  wa: 0812-3456-7890
Contoh 2:  WA: (0812) 3456-7890
Contoh 3:  WhatsApp: 0812 3456 7890
Contoh 4:  Hub: 62812345678
Contoh 5:  Minat: +62 812 345 678
Contoh 6:  Kontak: +62-812-345-678
Contoh 7:  0812345678
Contoh 8:  (0812) 345-678
```

---

## ⚠️ Edge Cases & Limitations

### Case 1: Multiple Nomor Dalam 1 Postingan
```
Text: "wa: 0812-111-1111 atau 0812-222-2222"
Output: "08121111111"  ← Ambil yang pertama
```
**Note:** Fungsi ambil nomor **PERTAMA** saja yang ditemukan.

### Case 2: Nomor Tidak Lengkap
```
Text: "wa: 081"
Output: ""  ← Regex butuh minimal 9-14 digit
```

### Case 3: Nomor Palsu
```
Text: "wa: 1234567890"  (tidak mulai 08/62/+62)
Output: ""  ← Tidak match
```

### Case 4: Nomor Lokal (Tanpa 08)
```
Text: "wa: 9922-8877"
Output: ""  ← Harus mulai 08/62/+62
```

---

## 🚀 Cara Menggunakan di Aplikasi

### Step 1: Script Jalankan Parser
```
Facebook Postingan → Parser.parse() → Extract WA → nomor_wa field
```

### Step 2: Data Tersimpan
```
JSON: posts_*.json  → nomor_wa: "08123456789O"
XLSX: posts_*.xlsx  → Column "No. WA" → "08123456789O"
```

### Step 3: Filter/Analisis Lebih Lanjut
```python
# Contoh: Filter postingan yang punya nomor WA
posts_with_wa = [p for p in posts if p["nomor_wa"]]

# Contoh: Group by nomor WA
from collections import Counter
Counter(p["nomor_wa"] for p in posts if p["nomor_wa"])
```

---

## 📈 Improvements yang Bisa Dilakukan

### 1. Multi-Nomor (Ambil Semua)
Saat ini hanya ambil nomor pertama. Bisa diupdate untuk ambil **semua nomor** dalam 1 postingan:
```python
def _extract_wa_all(text):
    pattern = r"(?:wa|whatsapp|hub|minat|kontak)\s*[:\-]?\s*((?:08|62|\+62)[\d\s\-()]{8,14})"
    matches = re.findall(pattern, text, re.IGNORECASE)
    return [re.sub(r"[\s\-()\[\]]", "", m) for m in matches]
```

### 2. Validasi Checksum (Luhn Algorithm)
Bisa tambah validasi apakah nomor valid secara format:
```python
def is_valid_whatsapp(number):
    # Bisa gunakan WhatsApp Business API untuk cek
    pass
```

### 3. Normalize Format
Convert semua ke satu format standar:
```python
def normalize_phone(number):
    # 08123456789O → +6281234567
    if number.startswith("0"):
        return "+62" + number[1:]
    return number
```

---

## 📞 Summary Tabel Singkat

| Format | Pattern | Contoh | Result |
|--------|---------|--------|--------|
| Prefix + Dash | Pattern 1 | `wa: 081-234-5678` | `08123456789O` |
| Prefix + Kurung | Pattern 1 | `wa: (081) 234-5678` | `08123456789O` |
| Tanpa Prefix | Pattern 2 | `0812345678` | `0812345678` |
| Kurung Saja | Pattern 3 | `(081) 234-5678` | `08123456789O` |
| International | Pattern 1 | `wa: +62 81 234-5678` | `+6281234567` |
| Tidak Ada | None | `harga 8juta` | `` (kosong) |

---

## 🔗 Related Functions

- `PostParser._extract_wa()` - Extract nomor WA
- `PostParser._extract_barang()` - Extract nama barang
- `PostParser._extract_harga()` - Extract harga
- `PostParser._extract_wa()` - Extract garansi
- Semua di class: [PostParser](scraper.py#L100-L220)

---

## 📌 Notes

- Update terakhir: 2026-02-20
- Status: Production Ready
- Compatibility: Python 3.8+
- Regex Engine: Python `re` module
