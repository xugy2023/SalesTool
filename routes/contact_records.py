# routes/contact_records.py
from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Customer, ContactRecord
import io
from flask import send_file
from openpyxl import Workbook


contact_bp = Blueprint("contact", __name__)

@contact_bp.route("/customers/<int:customer_id>")
def view_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    records = ContactRecord.query.filter_by(customer_id=customer_id).order_by(ContactRecord.date.desc()).all()
    return render_template("view_customer.html", customer=customer, records=records)


@contact_bp.route("/customers/<int:customer_id>/records/add", methods=["GET", "POST"])
def add_contact_record(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if request.method == "POST":
        content = request.form["content"]
        new_record = ContactRecord(customer_id=customer_id, content=content)
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for("contact.view_customer", customer_id=customer_id))

    return render_template("add_contact_record.html", customer=customer)

@contact_bp.route("/records/<int:record_id>/edit", methods=["GET", "POST"])
def edit_contact_record(record_id):
    record = ContactRecord.query.get_or_404(record_id)
    if request.method == "POST":
        record.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("contact.view_customer", customer_id=record.customer_id))
    return render_template("edit_contact_record.html", record=record)

@contact_bp.route("/records/<int:record_id>/delete", methods=["POST"])
def delete_contact_record(record_id):
    record = ContactRecord.query.get_or_404(record_id)
    customer_id = record.customer_id
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for("contact.view_customer", customer_id=customer_id))




@contact_bp.route("/customers/<int:customer_id>/export_excel")
def export_contact_records_excel(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    records = ContactRecord.query.filter_by(customer_id=customer_id).order_by(ContactRecord.date).all()

    wb = Workbook()
    ws = wb.active
    ws.title = f"{customer.name}联系记录"

    # 表头
    ws.append(["日期", "联系内容"])

    for record in records:
        ws.append([
            record.date.strftime("%Y-%m-%d %H:%M"),
            record.content
        ])

    # 内存导出为字节流
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"{customer.name}_联系记录.xlsx"
    return send_file(output, as_attachment=True, download_name=filename, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@contact_bp.route("/export_all_records_excel")
def export_all_records_excel():
    from openpyxl import Workbook
    import io
    from flask import send_file

    records = ContactRecord.query.join(Customer).order_by(ContactRecord.date.desc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "所有联系记录"

    # 表头
    ws.append(["客户姓名", "联系方式", "联系时间", "联系内容"])

    for record in records:
        ws.append([
            record.customer.name,
            record.customer.phone or "",
            record.date.strftime("%Y-%m-%d %H:%M"),
            record.content
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="所有客户联系记录.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
