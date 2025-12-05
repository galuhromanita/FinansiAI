from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from fastapi.responses import FileResponse
from app.services.report_generator import generate_pdf
import os, json

router = APIRouter()

@router.get("/download_pdf")
def download_pdf(request: Request):
    laporan_path = request.session.get("laporan_path")
    hasil = json.load(open(laporan_path, "r", encoding="utf-8"))

    pdf_path = f"app/reports/Laporan_{hasil['NamaUsaha']}_{hasil['Bulan']}.pdf"
    generate_pdf(hasil, pdf_path)

    return FileResponse(pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))
