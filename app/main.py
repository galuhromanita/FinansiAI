from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
import os

from app.routers import landing, dashboard, upload, process, laporan, pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")
TEMPLATES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "templates")
)
STATIC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "static")
)

print("STATIC_DIR =", STATIC_DIR)

app = FastAPI()

# 1. PROXY HEADERS (AGAR URL_FOR MEMAKAI HTTPS DI BELAKANG PROXY/RAILWAY)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 2. STATIC FILES — HARUS DIDAFTARKAN PALING AWAL
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 3. MIDDLEWARE
app.add_middleware(SessionMiddleware, secret_key="RAHASIA")

# 4. TEMPLATES
templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.state.templates = templates
print("TEMPLATES_DIR =", TEMPLATES_DIR)

#  5. ROUTERS
app.include_router(landing.router)
app.include_router(dashboard.router)
app.include_router(upload.router)
app.include_router(process.router)
app.include_router(laporan.router)
app.include_router(pdf.router)

# Cek apakah route static benar-benar terpasang
for r in app.routes:
    print("ROUTE:", r)
