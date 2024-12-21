from dashboard import create_usage_graph
from billing import billing_bp
from flask_login import login_required, current_user
from flask import render_template, request
import pandas as pd
import plotly.io as pio
from utils import get_prorated_data, filter_data_by_timeframe, create_usage_graph, create_cost_graph


@billing_bp.route('/', methods=['GET'])
@login_required
def billing_home():

    timeframe = request.args.get('timeframe', '12')
    
    if timeframe == 'all':
        timeframe = None
    else:
        timeframe = int(timeframe)

    data = get_prorated_data()
    filtered_data = filter_data_by_timeframe(data, timeframe)
    unit_fig = create_usage_graph(filtered_data, service_filter=["Electricity", "Gas", "Water"])
    cost_fig = create_cost_graph(filtered_data, service_filter=["Electricity", "Gas", "Water"])
    unit_graph_html = pio.to_html(unit_fig, full_html=False)
    cost_graph_html = pio.to_html(cost_fig, full_html=False)

    return render_template("billing_home.html", unit_graph_html=unit_graph_html, cost_graph_html=cost_graph_html, timeframe=timeframe)

