import csv
from flask import Blueprint, render_template, url_for, flash, request, redirect, jsonify, make_response, Response
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, DecimalField, DateField, DateTimeField, SubmitField, StringField
from wtforms.validators import InputRequired, ValidationError
from models import db, BillingData
from werkzeug.utils import secure_filename
from io import TextIOWrapper, BytesIO, StringIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

#Create Billing Blueprint
billing_bp = Blueprint('billing', __name__, template_folder='templates', static_folder='static')
headings = ("Upload Date", "Service", "Units", "Cost (£)", "Period Start Date", "Period End Date", "Actions")

import billing_home

#Bill Form
class BillForm(FlaskForm):
    
    service = StringField(validators=[InputRequired()])
    
    units = DecimalField(validators=[InputRequired()],places=1,
        render_kw={"placeholder": "0"})
    
    cost_gbp = DecimalField(validators=[InputRequired()],places=2,
        render_kw={"placeholder": "0"})
    
    start_date = DateField(format='%Y-%m-%d', validators=[InputRequired()])

    end_date = DateField(format='%Y-%m-%d', validators=[InputRequired()])

    submit = SubmitField("Upload")


@billing_bp.route('/add_billing', methods=['GET', 'POST'])
@login_required
def add_billing():
    
    form = BillForm()

    if form.validate_on_submit():
        new_bill = BillingData(
            user_id=current_user.id,
            service=form.service.data,
            units=form.units.data,
            cost_gbp=form.cost_gbp.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        db.session.add(new_bill)
        db.session.commit()
        flash("Billing data added successfully!", "success")
        return redirect(url_for('billing.view_billing'))
    else:
        submitted_date = request.form.get('date', None)

    return render_template('add_billing.html', form=form)

#Adding billing data using CSV file upload
@billing_bp.route('/upload_csv', methods=['POST'])
@login_required
def upload_csv():
    if 'csv_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('billing.add_billing'))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('billing.add_billing'))

    filename = secure_filename(file.filename)

    try:

        stream = TextIOWrapper(file.stream)
        stream.seek(0)
        csv_reader = csv.DictReader(stream)

        fieldnames = csv_reader.fieldnames
        if fieldnames and fieldnames[0].startswith('ï»¿'):
            fieldnames[0] = fieldnames[0].replace('ï»¿', '')
        
        row_count=0
        for row in csv_reader:
            row_count += 1
            service = row.get('service')
            units= row.get('units')
            cost_gbp = row.get('cost_gbp')
            start_date = row.get('start_date')
            end_date = row.get('end_date')

            if not (service and units and cost_gbp and start_date and end_date):
                flash(f"Missing data in row: {row}", "danger")
                continue

            try:

                new_bill = BillingData(
                    user_id=current_user.id,
                    service=str(service),
                    units=float(units),
                    cost_gbp=float(cost_gbp),
                    start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
                    end_date=datetime.strptime(end_date, '%Y-%m-%d').date()
                )
                db.session.add(new_bill)

            except ValueError as ve:
                flash(f"Error in row: {row}. Details: {str(ve)}", "danger")


        db.session.commit()
        print("Data committed successfully")
        flash('CSV uploaded and data added successfully!', 'success')

    except Exception as e:
        flash(f'Error processing CSV file: {str(e)}', 'danger')
        print(f"Error during commit: {e}")

    return redirect(url_for('billing.view_billing'))


@billing_bp.route('/delete_billing/<int:bill_id>', methods=['POST', 'GET'])
@login_required
def delete_billing(bill_id):
    bill = BillingData.query.filter_by(id=bill_id, user_id=current_user.id).first()
    if bill:
        db.session.delete(bill)
        db.session.commit()
        flash("Deletion was successful", 'success')
        return redirect(url_for('billing.view_billing'))
    flash("Record not found", 'danger')
    return redirect(url_for('billing.view_billing'))

@billing_bp.route('/view_billing', methods=['GET'])
@login_required
def view_billing():
    billing_data = BillingData.query.filter_by(user_id=current_user.id).all()
    return render_template('view_billing.html', billing_data=billing_data, headings=headings)


def get_export_data():
    billing_data=BillingData.query.filter_by(user_id=current_user.id).all()
    headings = ["Upload Date", "Service", "Units", "Cost(GBP)", "Start Date", "End Date"]
    data = [
        [
            bill.upload_date,
            bill.service,
            bill.units,
            bill.cost_gbp,
            bill.start_date,
            bill.end_date
        ]
        for bill in billing_data
    ]
    return headings, data

def get_timestamped_filename(base_name, extension):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return f"{base_name}_{timestamp}.{extension}"

@billing_bp.route('/export_pdf', methods=['GET'])
def export_pdf():
    headings, data = get_export_data()

    pdf_output = BytesIO()
    pdf = SimpleDocTemplate(pdf_output)
    elements = []

    table_data = [headings] + data
    table = Table(table_data)
    elements.append(table)
    pdf.build(elements)

    pdf_output.seek(0)
    response = Response(pdf_output.getvalue(), content_type='application/pdf')
    filename = get_timestamped_filename("billing_data", "pdf")
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'

    return response


@billing_bp.route('/export_csv', methods=['GET'])
def export_csv():
    headings, data = get_export_data()

    csv_output = StringIO()
    writer = csv.writer(csv_output)
    writer.writerow(headings)
    writer.writerows(data)

    csv_output.seek(0)
    response = Response(csv_output.getvalue().encode('utf-8-sig'), content_type='text/csv')
    filename = get_timestamped_filename("billing_data", "csv")
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'

    return response

