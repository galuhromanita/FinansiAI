from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def format_rupiah(value):
    return f"Rp {value:,.0f}".replace(",", ".")


def generate_pdf(hasil, output_path):
    # Gunakan ukuran A5 landscape (lebih lebar dari tinggi)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A5),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="HeaderTitle",
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="HeaderSubtitle",
            alignment=TA_CENTER,
            fontName="Helvetica",
            fontSize=10,
            leading=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ItalicSmall",
            alignment=TA_LEFT,
            fontName="Helvetica-Oblique",
            fontSize=8,
        )
    )

    elements = []

    # ===== HEADER =====
    header_data = [
        [Paragraph(f'<i>"{hasil["NamaUsaha"]}"</i>', styles["HeaderSubtitle"])],
        [Paragraph("LAPORAN KEUANGAN BULANAN", styles["HeaderTitle"])],
        [
            Paragraph(
                f'Untuk Bulan "{hasil["Bulan"]}" Tahun "{hasil["Tahun"]}"',
                styles["HeaderSubtitle"],
            )
        ],
    ]

    header_table = Table(header_data, colWidths=[landscape(A5)[0] - 50])  # full width minus margin
    header_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elements.append(header_table)
    elements.append(Spacer(1, 8))

    # ===== TABEL DATA =====
    # Sesuaikan lebar kolom agar pas dengan lebar A5 landscape (~210mm)
    data = [
        ["Keterangan", "", "Jumlah (Rp)"],
        ["Modal", "", format_rupiah(hasil["Modal"])],
        ["Pendapatan", "", format_rupiah(hasil["Pendapatan"])],
        ["", "", ""],
        ["Beban :", "", ""],
        ["", "Beban Usaha", format_rupiah(hasil["BebanUsaha"])],
        ["", "Beban Lain-lain", format_rupiah(hasil["BebanLain"])],
        ["", "Total Beban", format_rupiah(hasil["TotalBeban"])],
        ["", "", ""],
        ["Laba Bersih", "", format_rupiah(hasil["LabaBersih"])],
    ]

    # Lebar total = 210mm (A5 landscape), dikonversi ke point (1mm ≈ 2.8346pt)
    # Jadi sekitar 595pt total; kita sisakan margin
    table = Table(data, colWidths=[170, 190, 100])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("ALIGN", (0, 1), (1, -1), "LEFT"),
                ("ALIGN", (2, 1), (2, -1), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),

                # Warna highlight laba bersih
                ("BACKGROUND", (0, 9), (-1, 9), colors.lightgrey),
                ("FONTNAME", (0, 9), (-1, 9), "Helvetica-Bold"),
                ("LINEABOVE", (0, 9), (-1, 9), 1, colors.black),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 6))

    # ===== FOOTER =====
    elements.append(Paragraph("Laporan otomatis oleh FinansiAI", styles["ItalicSmall"]))

    # ===== BUILD PDF =====
    doc.build(elements)
