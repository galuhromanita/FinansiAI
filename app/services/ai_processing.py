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

    structured_rows = []
    modal = 0
    pendapatan = 0
    beban_usaha = 0
    beban_lain = 0
    warnings = []

    # 1️⃣ BENTUK DATA TERSTRUKTUR
    for row in raw:
        try:
            data = {
                "Tanggal": row[cols.index("Tanggal")],
                "Jenis Transaksi": row[cols.index("Jenis Transaksi")],
                "Keterangan": str(row[cols.index("Keterangan")]).lower(),
                "Jumlah": float(row[cols.index("Jumlah")])
            }
            structured_rows.append(data)
        except Exception as e:
            warnings.append(f"Baris tidak valid: {row}")
            continue

    # 2️⃣ HITUNG MANUAL (TANPA AI)
    for r in structured_rows:
        ket = r["Keterangan"]
        jumlah = r["Jumlah"]

        if "modal" in ket:
            modal += jumlah
        elif "penjualan" in ket or "pendapatan" in ket:
            pendapatan += jumlah
        elif "bahan" in ket or "alat" in ket or "gaji" in ket:
            beban_usaha += jumlah
        else:
            beban_lain += jumlah

    total_beban = beban_usaha + beban_lain
    laba_bersih = pendapatan - total_beban

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
        "Warnings": warnings
    }

    # 3️⃣ AI HANYA UNTUK NARASI (OPTIONAL)
    prompt = f"""
Berikut adalah laporan keuangan UMKM dalam format JSON:

{json.dumps(hasil_final, indent=2)}

Tugas Anda:
- Jelaskan kondisi keuangan usaha secara singkat
- Berikan insight
- Peringatkan jika laba bersih negatif

Jawab dalam 1 paragraf singkat, TANPA JSON.
"""

    # 4️⃣ Panggil Gemini hanya untuk insight naratif (dengan fallback jika gagal)
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        insight = get_text(response).strip()
        if not insight:
            raise ValueError("AI mengembalikan teks kosong")
    except Exception as e:
        print(f"AI insight error: {e}")
        insight = "Analisis otomatis tidak tersedia untuk saat ini, namun angka laporan keuangan sudah dihitung dari data Anda."

    hasil_final["InsightAI"] = insight

    return hasil_final
