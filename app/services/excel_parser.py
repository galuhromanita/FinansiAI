import pandas as pd
import numpy as np
import re

def clean_money(value):
    """Membersihkan format uang: '1.500.000' → 1500000."""
    if pd.isna(value):
        return 0
    if isinstance(value, (int, float)):
        return value
    value = str(value)
    value = value.replace(".", "").replace(",", "")
    return int(value) if value.isdigit() else 0


def extract_metadata(df):
    nama_usaha = ""
    bulan = ""
    tahun = ""

    for _, row in df.iterrows():
        for cell in row:
            if not isinstance(cell, str):
                continue

            text = cell.strip()

            # =========================
            # NAMA USAHA
            # =========================
            if "nama usaha" in text.lower():
                value = text.split(":", 1)[-1].strip()
                # 🔥 HILANGKAN PETIK
                nama_usaha = value.strip('"').strip("'")

            # =========================
            # CATATAN BULAN
            # =========================
            if "catatan bulan" in text.lower():
                value = text.split(":", 1)[-1].strip()

                # 🔥 AMBIL BULAN VALID
                bulan_match = re.search(
                    r"(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)",
                    value.lower()
                )

                # 🔥 AMBIL TAHUN VALID
                tahun_match = re.search(r"\b(19|20)\d{2}\b", value)

                if bulan_match:
                    bulan = bulan_match.group(1).capitalize()

                if tahun_match:
                    tahun = tahun_match.group(0)

    return nama_usaha, bulan, tahun

def parse_excel(filepath):

    df = pd.read_excel(filepath, header=None)
    
    nama_usaha, bulan, tahun = extract_metadata(df)

    # 1) BUANG SEMUA ROW KOSONG
    df = df.dropna(how="all")

    # 2) CARI ROW YANG MENGANDUNG HEADER SEBENARNYA
    header_row_index = None
    for i, row in df.iterrows():
        row_str = "".join(str(x).lower() for x in row.tolist())
        if "tanggal" in row_str and "jumlah" in row_str:
            header_row_index = i
            break

    if header_row_index is None:
        raise ValueError("Header transaksi tidak ditemukan dalam file Excel")

    # 3) PAKE ROW TERSEBUT SEBAGAI HEADER
    df.columns = df.iloc[header_row_index].tolist()
    df = df.iloc[header_row_index + 1 :]

    # 4) CONVERT NAMA HEADER KE FORMAT BAKU
    df.columns = [
        "Tanggal" if "tanggal" in str(c).lower() else
        "Jenis Transaksi" if "jenis transaksi" in str(c).lower() else
        "Keterangan" if "keterangan" in str(c).lower() else
        "Jumlah" if "jumlah" in str(c).lower() else
        str(c)
        for c in df.columns
    ]

    # 5) HANYA AMBIL 4 KOLOM PENTING
    keep_cols = ["Tanggal", "Jenis Transaksi", "Keterangan", "Jumlah"]
    df = df[[c for c in keep_cols if c in df.columns]]

    # 6) BERSIHKAN FORMAT UANG
    if "Tanggal" in df.columns:
        df["Tanggal"] = df["Tanggal"].astype(str)

    # 6.5) BERSIHKAN KOLOM JUMLAH
    if "Jumlah" in df.columns:
        df["Jumlah"] = df["Jumlah"].apply(clean_money)


    # 7) KONVERSI TANGGAL JIKA MAU
    # df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="ignore")

    parsed = {
        "columns": df.columns.tolist(),
        "raw_rows": df.values.tolist(),
        "meta" : {
            "NamaUsaha": nama_usaha,
            "Bulan": bulan,
            "Tahun": tahun
        }
    }

    print("\n===== CLEANED ROWS SAMPLE =====")
    print(parsed["raw_rows"][:5])
    print("===== END SAMPLE =====\n")

    return parsed

