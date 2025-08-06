# utils/pdf_generator.py
import pdfkit
from flask import make_response, render_template

def generate_pdf(filename, transcript, feedback, score=None):
    html = render_template(
        "result_pdf.html",
        filename=filename,
        transcript=transcript,
        feedback=feedback,
        score=score  # ✅ 新增
    )
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    options = {"encoding": "UTF-8"}
    pdf = pdfkit.from_string(html, False, configuration=config, options=options)

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}_分析报告.pdf"
    return response

