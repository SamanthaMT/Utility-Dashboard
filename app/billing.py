import csv
from flask import Blueprint, render_template, url_for, flash, request, redirect
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, DecimalField, DateField, DateTimeField, SubmitField
from wtforms.validators import InputRequired, ValidationError
from models import db, BillingData
from werkzeug.utils import secure_filename
from io import TextIOWrapper
from datetime import datetime

#Create Billing Blueprint
billing_bp = Blueprint('billing', __name__)

#Bill Form
class BillForm(FlaskForm):
    date = DateField(format='%Y-%m-%d', validators=[InputRequired()])
    
    usage_kwh = IntegerField(validators=[InputRequired()],
        render_kw={"placeholder": "0"})
    
    cost_gbp = DecimalField(validators=[InputRequired()], places=2,
        render_kw={"placeholder": "0"})

    submit = SubmitField("Upload")


@billing_bp.route('/add_billing', methods=['GET', 'POST'])
@login_required
def add_billing():
    
    form = BillForm()

    if form.validate_on_submit():
        new_bill = BillingData(
            user_id=current_user.id,
            date=form.date.data,
            usage_kwh=form.usage_kwh.data,
            cost_gbp=form.cost_gbp.data)
        db.session.add(new_bill)
        db.session.commit()
        flash("Billing data added successfully!", "success")
        return redirect(url_for('billing.view_billing'))
    else:
        submitted_date = request.form.get('date', None)

    return render_template('add_billing.html', form=form)

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
            date = row.get('date')
            usage_kwh = row.get('usage_kwh')
            cost_gbp = row.get('cost_gbp')

            if not (date and usage_kwh and cost_gbp):
                flash(f"Missing data in row: {row}", "danger")
                continue

            try:

                new_bill = BillingData(
                    user_id=current_user.id,
                    date=datetime.strptime(date, '%Y-%m-%d').date(),
                    usage_kwh=int(usage_kwh),
                    cost_gbp=float(cost_gbp)
                )
                db.session.add(new_bill)

            except ValueError as ve:
                flash(f"Error in row: {row}. Details: {str(ve)}", "danger")
                continue
        db.session.commit()
        flash('CSV uploaded and data added successfully!', 'success')

    except Exception as e:
        flash(f'Error processing CSV file: {str(e)}', 'danger')

    return redirect(url_for('billing.add_billing'))



@billing_bp.route('/view_billing', methods=['GET'])
@login_required
def view_billing():
    billing_data = BillingData.query.filter_by(user_id=current_user.id).all()
    return render_template('view_billing.html', billing_data=billing_data)