import os
import pandas as pd
import traceback
import google.generativeai as genai
import json

# # --- KONFIGURASI GEMINI ---
# genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyDfJB_kL0M7xlpec39UkbKgOzMwpSq1Bpo"))

# def analyze_data(data):
#     """Analisis transaksi keuangan menggunakan AI (Gemini)."""
#     try:
#         df = data["data"]
#         nama_usaha = data["nama_usaha"]
#         bulan_tahun = data["bulan"]

#         sample = df.to_markdown(index=False)

#         prompt = f"""
#         Kamu adalah AI akuntan profesional untuk aplikasi keuangan FinansiAI.

#         Berikut data transaksi keuangan harian sebuah usaha dalam format tabel markdown:
#         {sample}

#         Keterangan:
#         - Kolom "Jenis Transaksi" hanya berisi: Modal, Uang Masuk, Uang Keluar.
#         - Kolom "Keterangan" berisi deskripsi transaksi, misalnya: beli bahan, penjualan produk, bayar listrik, dll.
#         - Kolom "Jumlah (Rp)" berisi nilai uang.

#         Tugasmu:
#         1. Analisis transaksi di atas untuk menghasilkan rekap keuangan bulanan.
#         2. Klasifikasikan setiap transaksi "Uang Keluar" menjadi:
#            - Beban Usaha (operasional)
#            - Beban Lain-lain (non-operasional)
#         3. Hitung total:
#            Modal, Pendapatan, BebanUsaha, BebanLain, TotalBeban, dan LabaBersih.

#         Output hanya dalam format JSON valid seperti:
#         {{
#           "NamaUsaha": "{nama_usaha}",
#           "Bulan": "{bulan_tahun.split()[0]}",
#           "Tahun": "{bulan_tahun.split()[-1]}",
#           "Modal": 0,
#           "Pendapatan": 0,
#           "BebanUsaha": 0,
#           "BebanLain": 0,
#           "TotalBeban": 0,
#           "LabaBersih": 0
#         }}
#         """

#         model = genai.GenerativeModel("gemini-1.5-flash")
#         response = model.generate_content(prompt)
#         text = response.text.strip()

#         json_start = text.find("{")
#         json_end = text.rfind("}") + 1
#         json_str = text[json_start:json_end]

#         hasil = json.loads(json_str)
#         return hasil

#     except Exception as e:
#         print("❌ Error analisis AI:", str(e))
#         print(traceback.format_exc())
#         return {"error": str(e)}


# ==========================================
# 1️⃣ KLASIFIKASI OTOMATIS ATAU LOKAL
# ==========================================

def _local_rule_based(df):
    modal, pendapatan, beban_usaha, beban_lain = 0, 0, 0, 0
    for _, r in df.iterrows():
        jenis = str(r.get("Jenis Transaksi", "")).lower()
        jml = float(r.get("Jumlah (Rp)", 0))

        if "modal" in jenis:
            modal += jml
        elif "pendapatan" in jenis or "masuk" in jenis or "penjualan" in jenis:
            pendapatan += jml
        elif "beban" in jenis or "keluar" in jenis or "biaya" in jenis:
            if "lain" in jenis:
                beban_lain += jml
            else:
                beban_usaha += jml

    total_beban = beban_usaha + beban_lain
    laba_bersih = pendapatan - total_beban

    return {
        "modal": modal,
        "pendapatan": pendapatan,
        "beban_usaha": beban_usaha,
        "beban_lain": beban_lain,
        "total_beban": total_beban,
        "laba_bersih": laba_bersih,
        "used_model": "local-rule"
    }



def analyze_data(parsed):
    df = parsed["data"]
    nama_usaha = parsed["nama_usaha"]
    bulan_tahun = parsed["bulan"]

    # Gunakan logika lokal dulu
    result = _local_rule_based(df)

    hasil = {
        "NamaUsaha": nama_usaha,
        "Bulan": bulan_tahun.split()[0] if " " in bulan_tahun else bulan_tahun,
        "Tahun": bulan_tahun.split()[-1] if " " in bulan_tahun else "",
        "Modal": result["modal"],
        "Pendapatan": result["pendapatan"],
        "BebanUsaha": result["beban_usaha"],
        "BebanLain": result["beban_lain"],
        "TotalBeban": result["total_beban"],
        "LabaBersih": result["laba_bersih"]
    }

    print(f"✅ Analisis selesai untuk {nama_usaha} ({bulan_tahun})")
    return hasil
