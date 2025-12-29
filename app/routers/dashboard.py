from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
import os 

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_PATH = os.path.join(BASE_DIR, "frontend", "static", "template", "Template_Catatan_Transaksi_Harian.xlsx")

@router.get("/dashboard", name="dashboard")
def dashboard(request: Request):
    templates = request.app.state.templates
    
    error = request.session.pop("flash_error", None)

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            # setelah pop up error, kembali ke halaman upload
            "show_upload": True if error else False,
            "error": error
        }
    )

@router.get("/download_template", name="download_template")
def download_template():
    return FileResponse(
        TEMPLATE_PATH,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="Template_Catatan_Transaksi_Harian.xlsx"
    )