from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER

from app.services.excel_parser import parse_excel
from app.services.ai_processing import analyze_data

router = APIRouter()


@router.get("/process", name="process_file")
def process_file(request: Request, background_tasks: BackgroundTasks):
    templates = request.app.state.templates

    filepath = request.session.get("uploaded_file")
    if not filepath:
        # Jika tidak ada file, kembali ke dashboard dengan pesan error yang jelas
        request.session["flash_error"] = "Silakan upload file Excel terlebih dahulu."
        return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

    try:
        print(f"Parsing file: {filepath}")
        parsed = parse_excel(filepath)
        print(f"Berhasil Parsed data: {parsed}")

        print(f" Menganalisis data...")
        hasil = analyze_data(parsed)
        print(f"Berhasil menganalisis data: {hasil}")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Bedakan antara file tanpa data transaksi dan error lain (template salah, dsb.)
        if "NO_DATA_TRANSAKSI" in str(e):
            request.session["flash_error"] = (
                "File input tidak mengandung data transaksi sehingga proses analisis tidak dapat dilanjutkan."
            )
        else:
            # Untuk pengalaman pengguna yang konsisten,
            # anggap error lain di tahap proses sebagai template yang tidak sesuai.
            request.session["flash_error"] = (
                "File yang Anda unggah bukan template FINANSIAI"
            )

        # Kembali ke dashboard supaya pengguna melihat pesan error di halaman upload
        return RedirectResponse("/dashboard", status_code=HTTP_303_SEE_OTHER)

    # Jika proses berhasil, simpan hasil dan jadwalkan penghapusan file upload
    print(f" Saving hasil to session...")
    request.session["hasil"] = hasil

    # Hapus file Excel yang sudah diproses agar folder uploads tidak menumpuk
    uploaded_path = request.session.pop("uploaded_file", None)
    if uploaded_path:
        import os
        if os.path.exists(uploaded_path):
            background_tasks.add_task(os.remove, uploaded_path)

    print(f" Redirecting to /laporan")
    return RedirectResponse("/laporan", status_code=HTTP_303_SEE_OTHER)


# result = analyze_data(parse_excel)
# print("===== AI RESULT =====")
# print(result)
# print("=====================")
