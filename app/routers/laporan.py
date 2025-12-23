from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
import json, os

router = APIRouter()

@router.get("/laporan")
def laporan(request: Request):
    templates = request.app.state.templates

    hasil = request.session.get("hasil")
    if not hasil:
        # Jika tidak ada data hasil di session, kembalikan ke halaman upload (dashboard)
        return RedirectResponse("/dashboard")

    return templates.TemplateResponse(
        "laporan.html",
        {
            "request": request,
            "hasil": hasil
        }
    )



