from flask import Blueprint, render_template
from flask_login import login_required, current_user
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from models import BillingData
from sqlalchemy import func, extract
from calendar import monthrange
from datetime import date, timedelta
from utils import get_prorated_data, filter_data_by_timeframe, create_usage_graph

#Create dashboard blueprint
dashboard_bp = Blueprint('dashboard',__name__)


@dashboard_bp.route('', methods=['GET'])
@login_required
def dashboard():
    data = get_prorated_data()
    year_overview = filter_data_by_timeframe(data, 12)
    fig = create_usage_graph(year_overview)
    unit_graph_html = pio.to_html(fig, full_html=False)

    return render_template("dashboard.html", unit_graph_html=unit_graph_html)
