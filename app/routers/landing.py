from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/", name="landing")
def landing(request: Request):
    templates = request.app.state.templates
    
    # landing TIDAK BOLEH mengambil error, biarkan home.html yang menampilkan error
    return templates.TemplateResponse(
        "landing.html",
        {"request": request}
    )
