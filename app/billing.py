from flask import Blueprint, render_template, url_for, flash, request, redirect
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, DecimalField, DateField, DateTimeField, SubmitField
from wtforms.validators import InputRequired, ValidationError
from models import db, BillingData


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
        print("Errors: ", form.errors)
        print("submitted date: ", {submitted_date})

    return render_template('add_billing.html', form=form)

@billing_bp.route('/view_billing', methods=['GET'])
@login_required
def view_billing():
    billing_data = BillingData.query.filter_by(user_id=current_user.id).all()
    return render_template('view_billing.html', billing_data=billing_data)