# components/buildings_at_risk_widget.py
from dash import dcc, html
import pandas as pd

def create_buildings_at_risk_widget(buildings_df):
    """
    Calculates the number of buildings at risk from flooding and creates a KPI widget.
    """
    risk_cols = ["Watercourses_Risk", "Rivers_risk", "Sea_risk"]
    
    # Check if the dataframe and required columns exist
    if not buildings_df.empty and all(col in buildings_df.columns for col in risk_cols):
        # Drop rows where all risk columns are null, then count the rest
        at_risk_buildings = buildings_df.dropna(subset=risk_cols, how='all')
        num_at_risk = len(at_risk_buildings)
    else:
        num_at_risk = 0

    # Create the widget content
    content = html.Div(
        style={'textAlign': 'center', 'paddingTop': '20px'},
        children=[
            dcc.Markdown("#### Total Number of Buildings at Flood Risk"),
            html.H2(f"{num_at_risk:,}", style={'fontSize': '48px', 'margin': '0'})
        ]
    )
    
    return content
