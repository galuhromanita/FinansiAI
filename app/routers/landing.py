from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/", name="landing")
def landing(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "landing.html",
        {"request": request}
    )
