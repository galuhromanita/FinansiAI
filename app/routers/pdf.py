from fastapi import APIRouter, Request, BackgroundTasks
from starlette.responses import RedirectResponse
from fastapi.responses import FileResponse
from app.services.report_generator import generate_pdf
import os
import tempfile
from pathlib import Path

router = APIRouter()

@router.get("/download_pdf")
def download_pdf(request: Request, background_tasks: BackgroundTasks):
    # Ambil hasil langsung dari session (di-set di /process)
    hasil = request.session.get("hasil")
    if not hasil:
        # Jika tidak ada data laporan di session, kembali ke halaman laporan/upload
        return RedirectResponse("/laporan")

    # Gunakan folder temporary yang writable di semua environment (termasuk Railway)
    tmp_base = Path(tempfile.gettempdir()) / "finansiai_reports"
    tmp_base.mkdir(parents=True, exist_ok=True)

    pdf_filename = f"Laporan_{hasil['NamaUsaha']}_{hasil['Bulan']}.pdf"
    pdf_path = tmp_base / pdf_filename

    # Generate PDF ke lokasi ini
    generate_pdf(hasil, str(pdf_path))

    # Ambil path file Excel yang di-upload sebelumnya (disimpan di session oleh /upload)
    uploaded_path = request.session.pop("uploaded_file", None)

    # Setelah PDF dikirim ke pengguna, hapus file Excel dan PDF agar tidak menumpuk di storage
    if uploaded_path and os.path.exists(uploaded_path):
        background_tasks.add_task(os.remove, uploaded_path)

    if pdf_path.exists():
        # Hapus PDF setelah response selesai dikirim
        background_tasks.add_task(os.remove, str(pdf_path))

    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        filename=pdf_filename,
    )
