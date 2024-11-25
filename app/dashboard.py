from flask import Blueprint, render_template
from flask_login import login_required, current_user
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from models import BillingData
from sqlalchemy import func, extract

#Create dashboard blueprint
dashboard_bp = Blueprint('dashboard',__name__)

#Grouping data into months and finding total
date = BillingData.date

def get_monthly_data():
    results = BillingData.query.with_entities(
        extract('year', BillingData.date).label('year'),
        extract('month', BillingData.date).label('month'),
        func.sum(BillingData.usage_kwh).label('total_kwh'),
        func.sum(BillingData.cost_gbp).label('total_cost')
    ).filter(
        BillingData.user_id == current_user.id
    ).group_by(
        extract('year', date),
        extract('month', date)
    ).order_by(
        extract('year', date),
        extract('month', date)
    ).all()

    return results

#Create graph
def create_interactive_plot(dataframe):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dataframe["formatted_date"],
        y=dataframe["total_kwh"],
        mode="lines+markers",
        name="Usage (kWh)",
        hoverinfo="text",
        text=[f"Month: {date}<br>Usage: {kwh} kWh" for date, kwh in zip(dataframe["formatted_date"], dataframe["total_kwh"])]
    ))

    fig.update_layout(
        title="Energy Usage",
        xaxis_title= "Month",
        yaxis_title="kWh",
        legend_title="Metrics",
        template="plotly_dark"
    )

    return fig

@dashboard_bp.route('')
@login_required
def dashboard():
    results = get_monthly_data()

    monthly_data = []
    for year, month, total_kwh, total_cost in results:
        monthly_data.append({
            'year': int(year),
            'month': int(month),
            'formatted_date': f"{int(year)}-{int(month):02d}",
            'total_kwh': total_kwh,
            'total_cost': total_cost
        })

#Populate graph with data from table containing bills
    df = pd.DataFrame(monthly_data)

    print("dashboard reached")
    print(pd)
    fig = create_interactive_plot(df)
    graph_html = pio.to_html(fig, full_html=False)

    return render_template("dashboard.html", graph_html=graph_html)