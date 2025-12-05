import pandas as pd
import numpy as np

def clean_money(value):
    """Membersihkan format uang: '1.500.000' → 1500000."""
    if pd.isna(value):
        return 0
    if isinstance(value, (int, float)):
        return value
    value = str(value)
    value = value.replace(".", "").replace(",", "")
    return int(value) if value.isdigit() else 0


def parse_excel(filepath):
    df = pd.read_excel(filepath, header=None)

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
        "Keterangan" if "keterangan" in str(c).lower() else
        "Jumlah" if "jumlah" in str(c).lower() else
        "Kategori" if "kategori" in str(c).lower() else
        str(c)
        for c in df.columns
    ]

    # 5) HANYA AMBIL 4 KOLOM PENTING
    keep_cols = ["Tanggal", "Keterangan", "Jumlah", "Kategori"]
    df = df[[c for c in keep_cols if c in df.columns]]

    # 6) BERSIHKAN FORMAT UANG
    if "Tanggal" in df.columns:
        df["Tanggal"] = df["Tanggal"].astype(str)

    # 7) KONVERSI TANGGAL JIKA MAU
    # df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="ignore")

    parsed = {
        "columns": df.columns.tolist(),
        "raw_rows": df.values.tolist()
    }

    print("\n===== CLEANED ROWS SAMPLE =====")
    print(parsed["raw_rows"][:5])
    print("===== END SAMPLE =====\n")

    return parsed
