from fastapi import APIRouter, Request, BackgroundTasks
from starlette.responses import RedirectResponse
from fastapi.responses import FileResponse
from app.services.report_generator import generate_pdf
import os

router = APIRouter()

@router.get("/download_pdf")
def download_pdf(request: Request, background_tasks: BackgroundTasks):
    # Ambil hasil langsung dari session (di-set di /process)
    hasil = request.session.get("hasil")
    if not hasil:
        # Jika tidak ada data laporan di session, kembali ke halaman laporan/upload
        return RedirectResponse("/laporan")

    pdf_path = f"app/reports/Laporan_{hasil['NamaUsaha']}_{hasil['Bulan']}.pdf"
    generate_pdf(hasil, pdf_path)

    # Ambil path file Excel yang di-upload sebelumnya (disimpan di session oleh /upload)
    uploaded_path = request.session.pop("uploaded_file", None)

    # Setelah PDF dikirim ke pengguna, hapus file Excel dan PDF agar tidak menumpuk di storage
    if uploaded_path and os.path.exists(uploaded_path):
        background_tasks.add_task(os.remove, uploaded_path)

    if os.path.exists(pdf_path):
        background_tasks.add_task(os.remove, pdf_path)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path),
    )
