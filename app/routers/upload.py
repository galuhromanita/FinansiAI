from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
import os
import pandas as pd

router = APIRouter()

UPLOAD_FOLDER = "app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(None)):

    # ======================================================
    # A) CEK APAKAH ADA FILE YANG DIUPLOAD
    # ======================================================
    if file is None:
        request.session["flash_error"] = "Silakan pilih file terlebih dahulu."
        return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

    filename = os.path.basename(file.filename)

    # ======================================================
    # B) CEK EKSTENSI FILE
    # ======================================================
    if not filename.lower().endswith(".xlsx"):
        request.session["flash_error"] = "Format file harus .xlsx!"
        return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

    # ======================================================
    # C) CEK UKURAN FILE
    # ======================================================
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        request.session["flash_error"] = "File Anda terlalu besar, maksimal 2MB"
        return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

    # Reset file pointer agar bisa dibaca ulang
    await file.seek(0)

    # ======================================================
    # D) SIMPAN FILE SEMENTARA
    # ======================================================
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(save_path, "wb") as f:
        f.write(content)

    # ======================================================
    # E) VALIDASI: APAKAH INI TEMPLATE FINANSIAI?
    # ======================================================
    try:
        df = pd.read_excel(save_path, header=None)
    except:
        request.session["flash_error"] = "File tidak dapat dibaca, pastikan file Excel valid."
        return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

    # Cek apakah ada baris header yang memuat kata kunci template
    found_header = False
    for row in df.values.tolist():
        row_str = "".join([str(x).lower() for x in row])
        if "tanggal" in row_str and "jumlah" in row_str:
            found_header = True
            break

    if not found_header:
        request.session["flash_error"] = "File yang Anda unggah bukan template FINANSIAI"
        return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

    # ======================================================
    # F) SIMPAN PATH FILE UNTUK DIPROSES DI /process
    # ======================================================
    request.session["uploaded_file"] = save_path

    # Redirect ke loading
    return RedirectResponse("/loading", status_code=HTTP_303_SEE_OTHER)


@router.get("/loading")
def loading_page(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse("loading.html", {"request": request})
