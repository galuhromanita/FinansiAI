from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from services.excel_parser import parse_excel
from services.ai_processing import analyze_data
from services.report_generator import generate_pdf

app = Flask(__name__)
app.secret_key = "rahasia_super_aman"

# Batas ukuran file: 2 MB
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

# === ERROR HANDLER ===
@app.errorhandler(413)
def request_entity_too_large(error):
    flash("Ukuran file melebihi batas maksimal (2 MB).", "error")
    return redirect(url_for("dashboard"))

@app.errorhandler(Exception)
def handle_general_error(e):
    flash(f"Terjadi kesalahan tidak terduga: {str(e)}", "error")
    return redirect(url_for("dashboard"))


# === ALLOWED FILE ===
ALLOWED_EXTENSIONS = {"xlsx"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# === ROUTES ===
UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/download-template')
def download_template():
    template_path = os.path.join('templates-excel', 'Template_Input_Transaksi.xlsx')
    if not os.path.exists(template_path):
        flash("File template tidak ditemukan.", "error")
        return redirect(url_for("dashboard"))
    return send_file(template_path, as_attachment=True)


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')

    if not file or file.filename == "":
        flash("Silakan pilih file transaksi terlebih dahulu.", "error")
        return redirect(url_for("dashboard"))

    if not allowed_file(file.filename):
        flash("Format file tidak didukung. Unggah file Excel (.xlsx).", "error")
        return redirect(url_for("dashboard"))

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        session['uploaded_file'] = filepath
    except Exception as e:
        flash(f"File tidak dapat disimpan: {str(e)}", "error")
        return redirect(url_for("dashboard"))

    return redirect(url_for('loading_page'))


@app.route('/loading')
def loading_page():
    return render_template('loading.html')


@app.route('/process')
def process_file():
    filepath = session.get('uploaded_file')
    if not filepath:
        flash("Tidak ada file yang diproses. Unggah ulang file Anda.", "error")
        return redirect(url_for('dashboard'))

    data = parse_excel(filepath)
    session['parsed_data'] = data

    hasil = analyze_data(data)
    session['laporan'] = hasil

    if 'error' in hasil:
        flash("Terjadi kesalahan saat analisis data dengan AI.", "error")
        return redirect(url_for('dashboard'))

    return redirect(url_for('laporan'))


@app.route('/laporan')
def laporan():
    hasil = session.get('laporan')
    if not hasil:
        return redirect(url_for('dashboard'))
    return render_template('laporan.html', hasil=hasil)


@app.route('/download_pdf')
def download_pdf():
    hasil = session.get('laporan')
    if not hasil:
        flash("Tidak ada laporan untuk diunduh.", "error")
        return redirect(url_for('dashboard'))

    pdf_path = os.path.join(REPORT_FOLDER, f"Laporan_{hasil['NamaUsaha']}_{hasil['Bulan']}.pdf")
    generate_pdf(hasil, pdf_path)
    return send_file(pdf_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
