from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
import json, os

router = APIRouter()

@router.get("/laporan")
def laporan(request: Request):
    templates = request.app.state.templates

    laporan_path = request.session.get("laporan_path")
    if not laporan_path or not os.path.exists(laporan_path):
        return RedirectResponse("/dashboard")

    hasil = json.load(open(laporan_path, "r", encoding="utf-8"))
    return templates.TemplateResponse("laporan.html",
                                     {"request": request, "hasil": hasil})
