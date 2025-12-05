from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER

from app.services.excel_parser import parse_excel
from app.services.ai_processing import analyze_data

router = APIRouter()

@router.get("/process", name="process_file")
def process_file(request: Request):
    templates = request.app.state.templates

    filepath = request.session.get("uploaded_file")
    if not filepath:
        return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

    try:
        parsed = parse_excel(filepath)
        hasil = analyze_data(parsed)

    except Exception as e:
        request.session["error"] = str(e)
        return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

    request.session["hasil"] = hasil
    return RedirectResponse("/laporan", status_code=HTTP_303_SEE_OTHER)
