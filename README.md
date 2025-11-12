# FinansiAI

Aplikasi web untuk menganalisis dan membuat laporan keuangan bulanan secara otomatis menggunakan AI.

## Fitur

- 📊 Upload file transaksi bulanan (Excel .xlsx)
- 🤖 Analisis data otomatis dengan Google Generative AI
- 📄 Generate laporan keuangan PDF
- 🎨 Dashboard interaktif dengan Tailwind CSS
- 🔐 Session management untuk keamanan data

## Teknologi

- **Backend**: FastAPI + Uvicorn
- **Frontend**: HTML, Tailwind CSS, Lucide Icons
- **Template Engine**: Jinja2
- **Data Processing**: Pandas, Openpyxl
- **PDF Generation**: ReportLab
- **AI**: Google Generative AI
- **Charts**: Plotly

## Instalasi

1. Clone repository ini
2. Masuk ke folder backend:

   ```bash
   cd backend
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variable untuk Google AI (optional, sesuaikan di `backend/services/ai_processing.py`):

   ```bash
   # Windows
   set GOOGLE_API_KEY=your_api_key_here

   # Linux/Mac
   export GOOGLE_API_KEY=your_api_key_here
   ```

## Cara Menjalankan

### Cara Cepat (Launcher di root)

```bash
python run.py
```

### Development Mode (Hot Reload)

```bash
python -m uvicorn backend.app:app --reload --port 8000
```

### Production Mode

```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Buka browser dan akses:

- Landing Page: http://127.0.0.1:8000/
- Dashboard: http://127.0.0.1:8000/dashboard
- Laporan: http://127.0.0.1:8000/laporan

## Struktur Folder

```
FinansiAI/
├── run.py                  # Launcher untuk menjalankan backend
├── backend/                # Backend FastAPI
│   ├── app.py              # Entry point FastAPI
│   ├── requirements.txt    # Python dependencies
│   ├── services/           # Business logic
│   │   ├── ai_processing.py    # AI analysis
│   │   ├── excel_parser.py     # Excel parsing
│   │   └── report_generator.py # PDF generation
│   ├── templates-excel/    # Excel template download
│   ├── uploads/            # Uploaded files (auto-created)
│   └── reports/            # Generated PDFs (auto-created)
├── frontend/               # Frontend assets
│   ├── templates/          # HTML templates (Jinja2)
│   │   ├── landing.html
│   │   ├── dashboard.html
│   │   ├── loading.html
│   │   └── laporan.html
│   └── static/             # CSS, images, JS
│       ├── css/
│       └── image/
├── uploads/                # Uploaded files (auto-created)
└── reports/                # Generated PDFs (auto-created)
```

## Endpoint API

| Method | Endpoint             | Deskripsi               |
| ------ | -------------------- | ----------------------- |
| GET    | `/`                  | Landing page            |
| GET    | `/dashboard`         | Dashboard upload        |
| GET    | `/download-template` | Download template Excel |
| POST   | `/upload`            | Upload file transaksi   |
| GET    | `/loading`           | Loading page            |
| GET    | `/process`           | Process uploaded file   |
| GET    | `/laporan`           | Lihat laporan hasil     |
| GET    | `/download_pdf`      | Download laporan PDF    |
| GET    | `/healthz`           | Health check            |

## Penggunaan

1. Buka halaman landing dan klik **Get Started**
2. Di dashboard, klik **Choose File** untuk melihat petunjuk
3. Download template Excel jika belum punya
4. Upload file Excel yang sudah diisi
5. Tunggu proses analisis AI
6. Lihat dan download laporan PDF

## Catatan Keamanan

- Batas upload file: **2 MB**
- Format yang diterima: **Excel (.xlsx)**
- Session menggunakan signed cookies
- Secret key disimpan di `app.py` (ganti untuk production!)

## Troubleshooting

### Error "Module not found"

```bash
pip install -r requirements.txt
```

### Error "Google API Key"

Pastikan sudah set environment variable atau hardcode di `backend/services/ai_processing.py`

### Port sudah digunakan

Ganti port di command uvicorn, misal `--port 8001`

## Lisensi

Project ini dibuat untuk keperluan akademik.
