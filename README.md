# FinansiAI

Proyek ini merupakan aplikasi web untuk pengolahan laporan keuangan menggunakan AI. Backend berada dalam folder `app/` dan frontend (template dan aset statis) berada dalam folder `frontend/`.

## Struktur Folder

```bash
FinansiAI/
├─ app/
│  ├─ main.py
│  ├─ __pycache__/
│  ├─ reports/
│  ├─ routers/
│  │  ├─ dashboard.py
│  │  ├─ landing.py
│  │  ├─ laporan.py
│  │  ├─ pdf.py
│  │  ├─ process.py
│  │  ├─ upload.py
│  │  └─ __pycache__/
│  ├─ services/
│  │  ├─ ai_processing.py
│  │  ├─ excel_parser.py
│  │  ├─ report_generator.py
│  │  └─ __pycache__/
│  └─ uploads/
├─ frontend/
│  ├─ static/
│  │  ├─ css/
│  │  │  └─ style.css
│  │  ├─ img/
│  │  └─ template/
│  └─ templates/
│     ├─ home.html
│     ├─ landing.html
│     ├─ laporan.html
│     └─ loading.html
```

## Cara Menjalankan (Contoh)

Silakan sesuaikan dengan konfigurasi proyek Anda.

```bash
# Masuk ke folder proyek
cd "SEMESTER 5/FinansiAI"

# (Opsional) Buat dan aktifkan virtual environment
python -m venv .venv
.venv\\Scripts\\activate

# Install dependensi (sesuaikan dengan requirements yang Anda miliki)
pip install -r requirements.txt

# Jalankan aplikasi (misal menggunakan FastAPI + Uvicorn)
uvicorn app.main:app --reload
```

Penjelasan lebih detail (misalnya alur upload file, proses AI, dan laporan) bisa ditambahkan di README ini sesuai kebutuhan Anda.
