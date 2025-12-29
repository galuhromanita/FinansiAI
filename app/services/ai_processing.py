def analyze_data(parsed_excel: dict):

    meta = parsed_excel.get("meta", {})
    raw = parsed_excel["raw_rows"]
    cols = parsed_excel["columns"]

    modal = 0
    pendapatan = 0
    beban_usaha = 0
    beban_lain = 0
    warnings = []

    # buat struktur data yang lebih mudah diproses
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

    # hitung sesuai 3 jenis transaksi
    for r in structured_rows:
        jenis = r["Jenis Transaksi"]
        ket = r["Keterangan"]
        jumlah = r["Jumlah"]

        # -------- modal --------
        if jenis == "modal":
            modal += jumlah

        # -------- uang masuk --------
        elif jenis == "uang masuk":

            # Jika seharusnya modal (pinjaman / setoran)
            if any(x in ket for x in ["pinjaman", "kredit", "bank", "modal"]):
                modal += jumlah
                warnings.append(
                    f"'{ket}' dikoreksi dari Uang Masuk menjadi MODAL."
                )
            else:
                pendapatan += jumlah

        # -------- uang keluar --------
        elif jenis == "uang keluar":

            if any(x in ket for x in ["bahan", "alat", "gaji", "listrik", "air", "sewa"]):
                beban_usaha += jumlah
            else:
                beban_lain += jumlah

        # -------- jenis tidak valid --------
        else:
            warnings.append(
                f"Jenis transaksi tidak dikenali: '{jenis}'"
            )

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
        "Warnings": warnings,
    }

    return hasil_final