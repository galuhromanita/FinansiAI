import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def get_text(response):
    """Fallback aman untuk mengambil teks dari response Gemini."""
    # 1) coba direct
    try:
        if response.text:
            return response.text
    except:
        pass

    # 2) coba lewat parts
    try:
        parts = response.candidates[0].content.parts
        if parts:
            p = parts[0]
            if hasattr(p, "text"):
                return p.text
    except:
        pass

    return ""


def extract_json(text):
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("Tidak ada JSON dalam output.")
    return json.loads(match.group(0))


def analyze_data(parsed_excel: dict):

    meta = parsed_excel.get("meta", {})
    raw = parsed_excel["raw_rows"]
    cols = parsed_excel["columns"]

    modal = 0
    pendapatan = 0
    beban_usaha = 0
    beban_lain = 0
    warnings = []

    # =========================
    # BENTUK DATA TERSTRUKTUR
    # =========================
    structured_rows = []
    for row in raw:
        try:
            structured_rows.append({
                "Tanggal": row[cols.index("Tanggal")],
                "Jenis Transaksi": str(row[cols.index("Jenis Transaksi")]).lower().strip(),
                "Keterangan": str(row[cols.index("Keterangan")]).lower(),
                "Jumlah": float(row[cols.index("Jumlah")])
            })
        except Exception:
            warnings.append(f"Baris tidak valid: {row}")

    # =========================
    # HITUNG SESUAI 3 JENIS TRANSAKSI
    # =========================
    for r in structured_rows:
        jenis = r["Jenis Transaksi"]
        ket = r["Keterangan"]
        jumlah = r["Jumlah"]

        # -------- MODAL --------
        if jenis == "modal":
            modal += jumlah

        # -------- UANG MASUK --------
        elif jenis == "uang masuk":

            # Jika seharusnya modal (pinjaman / setoran)
            if any(x in ket for x in ["pinjaman", "kredit", "bank", "modal"]):
                modal += jumlah
                warnings.append(
                    f"'{ket}' dikoreksi dari Uang Masuk menjadi MODAL."
                )
            else:
                pendapatan += jumlah

        # -------- UANG KELUAR --------
        elif jenis == "uang keluar":

            if any(x in ket for x in ["bahan", "alat", "gaji", "listrik", "air", "sewa"]):
                beban_usaha += jumlah
            else:
                beban_lain += jumlah

        # -------- JENIS TIDAK VALID --------
        else:
            warnings.append(
                f"Jenis transaksi tidak dikenali: '{jenis}'"
            )

    total_beban = beban_usaha + beban_lain
    laba_bersih = pendapatan - total_beban

    # =========================
    # HASIL FINAL
    # =========================
    hasil_final = {
        "NamaUsaha": meta.get("NamaUsaha", "Tidak Diketahui"),
        "Bulan": meta.get("Bulan", ""),
        "Tahun": meta.get("Tahun", ""),
        "Modal": modal,
        "Pendapatan": pendapatan,
        "BebanUsaha": beban_usaha,
        "BebanLain": beban_lain,
        "TotalBeban": total_beban,
        "LabaBersih": laba_bersih,
        "Warnings": warnings,
        "InsightAI": None   # sengaja null, tidak pakai AI
    }

    return hasil_final