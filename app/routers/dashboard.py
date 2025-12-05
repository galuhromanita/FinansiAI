from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
import os 

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_PATH = os.path.join(BASE_DIR, "frontend", "static", "template", "Template_Catatan_Transaksi_Harian.xlsx")

# @router.get("/dashboard")
# def dashboard(request: Request):
#     templates = request.app.state.templates
#     show_upload = bool(request.session.pop("show_upload", False))
#     def get_flashed_messages(with_categories=False):
#         # Expected shape in session: [('category', 'message'), ...]
#         flashes = request.session.pop('flashes', []) if 'flashes' in request.session else []
#         if with_categories:
#             return flashes
#         return [m for c, m in flashes]

#     context = {"request": request, "show_upload": show_upload, "get_flashed_messages": get_flashed_messages}
#     return templates.TemplateResponse("home.html", context)

@router.get("/dashboard", name="dashboard")
def dashboard(request: Request):
    templates = request.app.state.templates
    
    error = request.session.pop("flash_error", None)

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "show_upload": False,
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