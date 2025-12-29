from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
import os
import pandas as pd

router = APIRouter()

UPLOAD_FOLDER = "app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 2 * 1024 * 1024  


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(None)):

    if file is None:
        request.session["flash_error"] = "Silakan pilih file terlebih dahulu."
        return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

    filename = os.path.basename(file.filename)

    # harus excel 
    if not filename.lower().endswith(".xlsx"):
        request.session["flash_error"] = "Format file harus .xlsx!"
        return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

    # ukuran lebih dari 2MB
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        request.session["flash_error"] = "File Anda terlalu besar, maksimal 2MB"
        return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

    # reset file pointer agar bisa dibaca ulang
    await file.seek(0)

    # simpan file ke folder uploads (sementara)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(save_path, "wb") as f:
        f.write(content)

    # validasi template file
    try:
        df = pd.read_excel(save_path, header=None, engine="openpyxl")
    except Exception as e:
        print("[UPLOAD] Gagal membaca Excel:", e)
        request.session["flash_error"] = "File tidak dapat dibaca, pastikan file Excel valid."
        return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

    # cek apakah ada baris header yang memuat kata kunci template
    header_row_index = None
    for idx, row in enumerate(df.values.tolist()):
        row_str = "".join([str(x).lower() for x in row])
        if "tanggal" in row_str and "jumlah" in row_str:
            header_row_index = idx
            break

    if header_row_index is None:
        request.session["flash_error"] = "File yang Anda unggah bukan template FINANSIAI"
        return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

    # setelah header ditemukan, cek apakah masih ada data transaksi di bawahnya
    data_df = df.iloc[header_row_index + 1 :].copy()
    # anggap sel berisi hanya spasi sebagai kosong
    data_df = data_df.replace(r"^\s*$", pd.NA, regex=True)

    if data_df.dropna(how="all").empty:
        request.session["flash_error"] = (
            "File yang anda unggah masih kosong sehingga proses analisis tidak dapat dilanjutkan."
        )
        return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

    # simpan path file untuk diproses di /process
    request.session["uploaded_file"] = save_path

    # redirect ke loading
    return RedirectResponse("/loading", status_code=HTTP_303_SEE_OTHER)


@router.get("/loading")
def loading_page(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse("loading.html", {"request": request})
