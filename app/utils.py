from sqlalchemy import extract, func
from models import db, BillingData
from datetime import datetime

def get_monthly_costs(user_id):
    current_year = datetime.now().year
    monthly_data = db.session.query(
        extract('month', BillingData.date).label('month'),
            func.sum(BillingData.cost_gbp).label('total_cost')
   ).filter(
       BillingData.user_id == user_id,
       extract('year', BillingData.date) == current_year
   ).group_by('month').order_by('month').all()
    
    months = [row[0] for row in monthly_data]
    total_costs = [float(row[1]) for row in monthly_data]

    return months, total_costs







"""
#Adding stats

def calculate_monthly_summary(billing_data):

    df = pd.DataFrame(billing_data)

    df['date'] = pd.to_datetime(df['date'])

    total_cost = df['cost_usd'].sum()
    average_usage = df['usage_kwh'].mean()

    df['month'] = df['date'].dt.month
    peak_month = df.groupby('month')['usage_kwh'].sum().idxmax()

    return {
        'total_cost': total_cost,
        'average_usage': average_usage,
        'peak_month': peak_month
    }
"""