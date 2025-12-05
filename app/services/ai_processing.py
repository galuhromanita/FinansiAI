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

    raw = parsed_excel["raw_rows"]
    cols = parsed_excel["columns"]

    formatted_rows = []
    for i, row in enumerate(raw[:20], start=1):
        d = dict(zip(cols, row))
        formatted_rows.append(
            f"{i}) {d.get('Tanggal','')} | {d.get('Keterangan','')} | {d.get('Jumlah','')}"
        )

    data_text = "\n".join(formatted_rows)

    template = {
        "NamaUsaha": "",
        "Bulan": "",
        "Tahun": "",
        "Modal": 0,
        "Pendapatan": 0,
        "BebanUsaha": 0,
        "BebanLain": 0,
        "TotalBeban": 0,
        "LabaBersih": 0,
        "Warnings": []
    }

    prompt = f"""
Analisis daftar transaksi berikut dan kembalikan hanya JSON valid:

{json.dumps(template)}

Data:
{data_text}

Aturan:
- Modal = berisi 'modal'
- Pendapatan = 'penjualan' / 'pendapatan'
- BebanUsaha = pembelian bahan / alat usaha
- BebanLain = selain itu
- Jika ambigu → masukkan ke Warnings
Hanya jawab JSON.
"""

    # MODEL PRO (lebih stabil)
    model = genai.GenerativeModel("models/gemini-pro-latest")

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.0,
            "max_output_tokens": 4096,  # lebih tinggi
        }
    
    )
    text = get_text(response)

    if not text.strip():
        try:
            text = response.candidates[0].content.parts[0].text
        except:
            pass