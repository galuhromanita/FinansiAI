import pandas as pd
import re

def parse_excel(file_path):
    """Membaca template transaksi FinansiAI dari Excel."""
    try:
        raw_df = pd.read_excel(file_path, header=None)

        nama_usaha = None
        bulan = None
        for row in raw_df[0]:
            if isinstance(row, str):
                if re.search(r"Nama\s*Usaha", row, re.IGNORECASE):
                    nama_usaha = row.split(":")[-1].strip()
                elif re.search(r"Bulan", row, re.IGNORECASE):
                    bulan = row.split(":")[-1].strip()

        if not nama_usaha or not bulan:
            print("❌ Nama Usaha dan Bulan wajib diisi di template!")
            return None

        header_row_index = None
        for i, row in raw_df.iterrows():
            if any(isinstance(cell, str) and "Jenis Transaksi" in cell for cell in row):
                header_row_index = i
                break

        if header_row_index is None:
            print("❌ Tidak ditemukan header tabel transaksi.")
            return None

        df = pd.read_excel(file_path, header=header_row_index)

        expected_cols = {"Jenis Transaksi", "Keterangan", "Jumlah (Rp)"}
        if not expected_cols.issubset(df.columns):
            print("⚠️ Kolom tidak lengkap tapi lanjut parsing.")

        df = df.dropna(how='all')
        df = df[~df["Jenis Transaksi"].astype(str).str.contains("total", case=False, na=False)]

        if "Jumlah (Rp)" in df.columns:
            df["Jumlah (Rp)"] = pd.to_numeric(df["Jumlah (Rp)"], errors="coerce").fillna(0)

        print(f"✅ Data '{nama_usaha}' bulan '{bulan}' berhasil dibaca ({len(df)} baris).")
        return {"nama_usaha": nama_usaha, "bulan": bulan, "data": df}

    except Exception as e:
        print("❌ Error parsing Excel:", e)
        return None
