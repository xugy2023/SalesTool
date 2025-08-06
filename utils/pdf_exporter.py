# utils/pdf_exporter.py
import pdfkit
from flask import render_template, make_response

def generate_pdf(filename, transcript, feedback, score=None):
    html = render_template(
        "result_pdf.html",
        filename=filename,
        transcript=transcript,
        feedback=feedback,
        score=score
    )
    config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf = pdfkit.from_string(html, False, configuration=config, options={"encoding": "UTF-8"})

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}_分析报告.pdf'
    return response
