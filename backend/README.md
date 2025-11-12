# Backend API

Backend FastAPI untuk aplikasi FinansiAI.

## Struktur

```
backend/
├── app.py                  # Entry point FastAPI
├── requirements.txt        # Python dependencies
├── services/              # Business logic modules
│   ├── ai_processing.py    # Google Generative AI integration
│   ├── excel_parser.py     # Excel file parsing
│   └── report_generator.py # PDF report generation
├── templates-excel/       # Excel template for download
├── uploads/               # Uploaded user files (auto-created)
└── reports/               # Generated PDF reports (auto-created)
```

## Setup & Run

### Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Set environment variable (optional)

```bash
# Windows
set GOOGLE_API_KEY=your_api_key_here

# Linux/Mac
export GOOGLE_API_KEY=your_api_key_here
```

### Run development server

```bash
cd backend
python -m uvicorn app:app --reload --port 8000
```

### Run production server

```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

## API Endpoints

| Method | Endpoint             | Deskripsi                     |
| ------ | -------------------- | ----------------------------- |
| GET    | `/`                  | Landing page                  |
| GET    | `/dashboard`         | Dashboard upload              |
| GET    | `/download-template` | Download Excel template       |
| POST   | `/upload`            | Upload file transaksi (.xlsx) |
| GET    | `/loading`           | Loading page                  |
| GET    | `/process`           | Process uploaded file with AI |
| GET    | `/laporan`           | View analysis report          |
| GET    | `/download_pdf`      | Download PDF report           |
| GET    | `/healthz`           | Health check endpoint         |

## Configuration

- **Upload limit**: 2 MB
- **Allowed file types**: `.xlsx` only
- **Session**: Signed cookie-based (SessionMiddleware)
- **Secret key**: Set in `app.py` (change for production!)

## Dependencies

- **fastapi**: Modern web framework
- **uvicorn**: ASGI server
- **python-multipart**: File upload support
- **jinja2**: Template rendering
- **pandas**: Data processing
- **openpyxl**: Excel file handling
- **reportlab**: PDF generation
- **plotly**: Chart generation
- **google-generativeai**: AI analysis
- **itsdangerous**: Session security
