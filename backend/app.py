import os
import json
from typing import Optional, List, Tuple, Dict, Any

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from jinja2 import pass_context
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask

from backend.services.excel_parser import parse_excel
from backend.services.ai_processing import analyze_data
from backend.services.report_generator import generate_pdf
import os
SECRET_KEY = os.getenv("FINANSIAI_SECRET_KEY", "rahasia_super_aman")

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")
TEMPLATE_EXCEL_PATH = os.path.join(BASE_DIR, 'templates-excel', 'Template_Input_Transaksi.xlsx')

# Frontend paths (one level up -> frontend/)
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, "templates")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# === App ===
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# static and templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# ---- Flask-like helpers for Jinja ----
@pass_context
def flask_like_url_for(ctx, name: str, **params) -> str:
    request: Request = ctx["request"]
    # Map Flask's filename -> Starlette's path for static
    if name == "static" and "filename" in params:
        params = {"path": params.pop("filename")}
    url = request.url_for(name, **params)
    return str(url)

@pass_context
def get_flashed_messages(ctx, with_categories: bool = False):
    request: Request = ctx["request"]
    flashes: List[Tuple[str, str]] = request.session.pop("_flashes", [])
    if with_categories:
        return flashes
    return [msg for _, msg in flashes]

def flash(request: Request, message: str, category: str = "message") -> None:
    flashes: List[Tuple[str, str]] = request.session.get("_flashes", [])
    flashes.append((category, message))
    request.session["_flashes"] = flashes

# inject helpers into jinja
templates.env.globals["url_for"] = flask_like_url_for
templates.env.globals["get_flashed_messages"] = get_flashed_messages

# === Config ===
MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2 MB
ALLOWED_EXTENSIONS = {"xlsx"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# === Routes ===
@app.get("/", response_class=HTMLResponse, name="landing")
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse, name="dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/download-template", name="download_template")
async def download_template(request: Request):
    if not os.path.exists(TEMPLATE_EXCEL_PATH):
        flash(request, "File template tidak ditemukan.", "error")
        return RedirectResponse(url=request.url_for("dashboard"), status_code=303)
    return FileResponse(
        TEMPLATE_EXCEL_PATH,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(TEMPLATE_EXCEL_PATH),
    )

@app.post("/upload", name="upload_file")
async def upload_file(request: Request, file: UploadFile = File(None)):
    # Validate upload presence
    if file is None or not file.filename:
        flash(request, "Silakan pilih file transaksi terlebih dahulu.", "error")
        return RedirectResponse(url=request.url_for("dashboard"), status_code=303)

    # Validate extension
    if not allowed_file(file.filename):
        flash(request, "Format file tidak didukung. Unggah file Excel (.xlsx).", "error")
        return RedirectResponse(url=request.url_for("dashboard"), status_code=303)

    # Size guard using header first
    content_length = request.headers.get("content-length")
    try:
        if content_length and int(content_length) > MAX_UPLOAD_SIZE:
            flash(request, "Ukuran file melebihi batas maksimal (2 MB).", "error")
            return RedirectResponse(url=request.url_for("dashboard"), status_code=303)
    except Exception:
        pass

    # Save to disk
    try:
        # Read file content into disk
        safe_name = os.path.basename(file.filename)
        dest_path = os.path.join(UPLOAD_FOLDER, safe_name)
        with open(dest_path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
        # additional size check after write
        if os.path.getsize(dest_path) > MAX_UPLOAD_SIZE:
            os.remove(dest_path)
            flash(request, "Ukuran file melebihi batas maksimal (2 MB).", "error")
            return RedirectResponse(url=request.url_for("dashboard"), status_code=303)

        request.session["uploaded_file"] = dest_path
    except Exception as e:
        flash(request, f"File tidak dapat disimpan: {str(e)}", "error")
        return RedirectResponse(url=request.url_for("dashboard"), status_code=303)

    return RedirectResponse(url=request.url_for("loading_page"), status_code=303)

@app.get("/loading", response_class=HTMLResponse, name="loading_page")
async def loading_page(request: Request):
    return templates.TemplateResponse("loading.html", {"request": request})

@app.get("/process", name="process_file")
async def process_file(request: Request):
    filepath: Optional[str] = request.session.get("uploaded_file")
    if not filepath:
        flash(request, "Tidak ada file yang diproses. Unggah ulang file Anda.", "error")
        return RedirectResponse(url=request.url_for("dashboard"), status_code=303)

    data = parse_excel(filepath)
    if not data:
        flash(request, "Gagal membaca file. Pastikan format template sesuai.", "error")
        return RedirectResponse(url=request.url_for("dashboard"), status_code=303)

    # Simpan data transaksi mentah ke JSON (ephemeral)
    try:
        df = data.get("data")
        records: List[Dict[str, Any]] = []
        if df is not None:
            try:
                records = df.to_dict(orient="records")
            except Exception:
                # fallback defensif
                records = []

        json_payload = {
            "nama_usaha": data.get("nama_usaha"),
            "bulan": data.get("bulan"),
            "records": records,
        }
        base = os.path.splitext(os.path.basename(filepath))[0]
        json_path = os.path.join(UPLOAD_FOLDER, f"{base}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_payload, f, ensure_ascii=False)
        request.session["parsed_json_path"] = json_path
    except Exception as e:
        flash(request, f"Gagal menyimpan data JSON: {str(e)}", "error")
        return RedirectResponse(url=request.url_for("dashboard"), status_code=303)

    hasil = analyze_data(data)
    request.session["laporan"] = hasil

    # Hitung data grafik sederhana: total per Jenis Transaksi
    try:
        totals: Dict[str, float] = {"Modal": 0.0, "Uang Masuk": 0.0, "Uang Keluar": 0.0}
        for r in records:
            jenis = str(r.get("Jenis Transaksi", "")).strip()
            jumlah = float(r.get("Jumlah (Rp)", 0) or 0)
            if jenis in totals:
                totals[jenis] += jumlah
        chart_data = [
            {"label": k, "value": v} for k, v in totals.items()
        ]
        request.session["chart_data"] = chart_data
    except Exception:
        request.session["chart_data"] = []

    if isinstance(hasil, dict) and "error" in hasil:
        flash(request, "Terjadi kesalahan saat analisis data dengan AI.", "error")
        return RedirectResponse(url=request.url_for("dashboard"), status_code=303)

    return RedirectResponse(url=request.url_for("laporan"), status_code=303)

@app.get("/laporan", response_class=HTMLResponse, name="laporan")
async def laporan(request: Request):
    hasil = request.session.get("laporan")
    if not hasil:
        return RedirectResponse(url=request.url_for("dashboard"), status_code=303)
    chart_data = request.session.get("chart_data", [])
    return templates.TemplateResponse("laporan.html", {"request": request, "hasil": hasil, "chart_data": chart_data})

@app.get("/download_pdf", name="download_pdf")
async def download_pdf(request: Request):
    hasil = request.session.get("laporan")
    if not hasil:
        flash(request, "Tidak ada laporan untuk diunduh.", "error")
        return RedirectResponse(url=request.url_for("dashboard"), status_code=303)

    pdf_path = os.path.join(REPORT_FOLDER, f"Laporan_{hasil['NamaUsaha']}_{hasil['Bulan']}.pdf")
    generate_pdf(hasil, pdf_path)

    # Siapkan cleanup ephemeral files setelah diunduh
    uploaded_path: Optional[str] = request.session.get("uploaded_file")
    parsed_json_path: Optional[str] = request.session.get("parsed_json_path")

    # Bersihkan session lebih dulu agar cookie diperbarui ke klien
    for k in ["uploaded_file", "parsed_json_path", "laporan", "chart_data"]:
        if k in request.session:
            request.session.pop(k, None)

    def cleanup():
        # hapus file pdf dan file sementara
        for p in [pdf_path, uploaded_path, parsed_json_path]:
            try:
                if p and os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

    background = BackgroundTask(cleanup)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path),
        background=background,
    )

# === Exception handlers ===
@app.exception_handler(Exception)
async def handle_general_error(request: Request, exc: Exception):
    # Log can be added here
    flash(request, f"Terjadi kesalahan tidak terduga: {str(exc)}", "error")
    return RedirectResponse(url=request.url_for("dashboard"), status_code=303)

# Optional: root health check
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
