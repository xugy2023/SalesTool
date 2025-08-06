# routes/customers.py
from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash
from models import db, Customer
import pandas as pd
import io
import os

customers_bp = Blueprint("customers", __name__)


@customers_bp.route("/customers")
def list_customers():
    filter_status = request.args.get("filter_status", "")
    if filter_status:
        customers = Customer.query.filter_by(status=filter_status).all()
    else:
        customers = Customer.query.all()
    return render_template("customers.html", customers=customers, filter_status=filter_status)


@customers_bp.route("/customers/add", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        company = request.form["company"]
        status = request.form["status"]

        new_customer = Customer(name=name, phone=phone, company=company, status=status)
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for("customers.list_customers"))

    return render_template("add_customer.html")


@customers_bp.route("/customers/import", methods=["GET", "POST"])
def import_customers():
    if request.method == "POST":
        file = request.files["file"]
        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                customer = Customer(
                    name=row.get("name", ""),
                    phone=row.get("phone", ""),
                    company=row.get("company", ""),
                    status=row.get("status", "")
                )
                db.session.add(customer)
            db.session.commit()
            return redirect(url_for("customers.list_customers"))

    return render_template("import_customers.html")


@customers_bp.route("/customers/export")
def export_customers():
    customers = Customer.query.all()
    data = [{"name": c.name, "phone": c.phone, "company": c.company, "status": c.status} for c in customers]
    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="customers.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
