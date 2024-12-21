from sqlalchemy import extract, func
from models import db, BillingData
from datetime import datetime, date, timedelta
from flask_login import current_user
from calendar import monthrange
import pandas as pd
import plotly.graph_objects as go


#Prorating data
def prorate_units(start_date, end_date, total_units, total_cost) :
   
    prorated_unit_data = []
    current_date = start_date

#Calculating overlap between bill period and current month
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        days_in_month = monthrange(year, month)[1]

        month_start = date(year, month, 1)
        month_end = date(year, month, days_in_month)

        overlap_start = max(current_date, month_start)
        overlap_end = min(end_date, month_end)
        overlap_days = (overlap_end - overlap_start).days + 1

#Calculating daily usage and prorated usage for the month
        days_in_period = (end_date - start_date).days + 1
        daily_units = total_units / days_in_period
        prorated_units = daily_units * overlap_days

        daily_cost = total_cost / days_in_period
        prorated_cost = daily_cost * overlap_days

        prorated_unit_data.append({
            'year': year,
            'month': month,
            'service': None,
            'prorated_units': prorated_units,
            'prorated_cost': prorated_cost
        })

        current_date = month_end + timedelta(days=1)

    return prorated_unit_data

#Grouping data
def get_prorated_data():
    bills = BillingData.query.filter(BillingData.user_id == current_user.id).all()
    prorated_results = []

    for bill in bills:
        prorated_data = prorate_units(bill.start_date, bill.end_date, bill.units, bill.cost_gbp)
        for entry in prorated_data:
            entry['service'] = bill.service
        prorated_results.extend(prorated_data)

    return pd.DataFrame(prorated_results)

#Filtering data to requested time period
def filter_data_by_timeframe(dataframe, months_back):
    today = date.today()

    if months_back:
        start_date = today - timedelta(days=30 * months_back)
    else:
        start_date = None

    dataframe['formatted_date'] = dataframe.apply(lambda row: date(int(row['year']), int(row['month']), 1), axis=1)
    dataframe['formatted_date'] = pd.to_datetime(dataframe['formatted_date']).dt.date

    if start_date:
        return dataframe[(dataframe['formatted_date'] >= start_date) & (dataframe['formatted_date'] <= today)]
    else:
        return dataframe

#Create graph displaying units used
def create_usage_graph(dataframe, service_filter=None):
    fig = go.Figure()

    if dataframe.empty:
        fig.add_annotation(
            text="No data available",
            showarrow=False,
            font=dict(size=20)
        )
    else:
#Graph showing individual services
        if service_filter:
            for service in service_filter:
                service_data = dataframe[dataframe['service'] == service].groupby('formatted_date', as_index=False).agg(
                    total_units=('prorated_units', 'sum')
                )
                fig.add_trace(go.Scatter(
                    x=service_data["formatted_date"],
                    y=service_data["total_units"],
                    mode="lines+markers",
                    name=f"{service} Units",
                    hoverinfo="text",
                    text=[f"Month: {formatted_date}<br>Usage: {units}" for formatted_date, units in zip(service_data["formatted_date"], service_data["total_units"])]
                ))
        else:
#Graph showing total units across all services
            combined_data = dataframe.groupby('formatted_date', as_index=False).agg(
                total_units=('prorated_units', 'sum')
            )
            fig.add_trace(go.Scatter(
                x=combined_data["formatted_date"],
                y=combined_data["total_units"],
                mode="lines+markers",
                name="Total Units",
                hoverinfo="text",
                text=[f"Month: {formatted_date}<br>Usage: {units} units" for formatted_date, units in zip(combined_data["formatted_date"], combined_data["total_units"])]
            ))
    
    fig.update_layout(
        title="Energy Usage",
        xaxis_title= "Month",
        yaxis_title="Units",
        legend_title="Metrics",
        template="plotly_dark"
    )

    return fig

#Create graph displaying cost
def create_cost_graph(dataframe, service_filter):
    fig = go.Figure()

    if dataframe.empty:
        fig.add_annotation(
            text="No data available",
            showarrow=False,
            font=dict(size=20)
        )
    else:
        for service in service_filter:
            service_data = dataframe[dataframe['service'] == service].groupby('formatted_date', as_index=False).agg(
                total_cost=('prorated_cost', 'sum')
            )
            fig.add_trace(go.Scatter(
                x=service_data["formatted_date"],
                y=service_data["total_cost"],
                mode="lines+markers",
                name=f"{service} Cost",
                hoverinfo="text",
                text=[f"Month: {formatted_date}<br>Cost: {cost_gbp}" for formatted_date, cost_gbp in zip(service_data["formatted_date"], service_data["total_cost"])]
            ))

    fig.update_layout(
        title="Energy Costs",
        xaxis_title= "Month",
        yaxis_title="Cost",
        legend_title="Metrics",
        template="plotly_dark"
    )

    return fig

