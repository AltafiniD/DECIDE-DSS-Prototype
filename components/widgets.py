# components/widgets.py
from dash import dcc, html
import pandas as pd
from .crime_widget import create_crime_histogram_figure
from .network_widget import create_network_histogram_figure
from .flood_risk_widget import create_flood_risk_pie_chart

def get_widgets(dataframes, color_map):
    """
    Defines a list of all widgets to be displayed in the slide-over panel.
    """
    crime_df = dataframes.get('crime_points', pd.DataFrame())
    network_df = dataframes.get('network', pd.DataFrame())
    buildings_df = dataframes.get('buildings', pd.DataFrame())
    
    initial_crime_fig = create_crime_histogram_figure(crime_df, color_map)
    
    initial_metric = 'NAIN' if 'NAIN' in network_df.columns else None
    initial_metric_series = network_df[initial_metric] if initial_metric and not network_df.empty else pd.Series()
    initial_network_fig = create_network_histogram_figure(initial_metric_series, initial_metric)

    # --- MODIFIED: Create initial figure with no title ---
    initial_flood_risk_fig = create_flood_risk_pie_chart(buildings_df, 'Sea_risk', title="")


    crime_statistics_widget = {
        # --- MODIFIED: Adjusted width for 2-column grid ---
        "size": (2, 3),
        "content": [
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'},
                children=[
                    dcc.Markdown(id="crime-widget-title", children="#### Crime Statistics for Cardiff"),
                    html.Button("Clear Selection", id="clear-crime-filter-btn", n_clicks=0, style={'fontSize': '12px'})
                ]
            ),
            dcc.Graph(id="crime-bar-chart", figure=initial_crime_fig, style={'height': '85%'})
        ]
    }

    network_statistics_widget = {
        # --- MODIFIED: Adjusted width for 2-column grid ---
        "size": (2, 2),
        "content": [
            dcc.Graph(id="network-histogram-chart", figure=initial_network_fig, style={'height': '100%'})
        ]
    }

    flood_risk_widget = {
        # --- MODIFIED: Set to 1 column width to be half of the others ---
        "size": (1, 2),
        "content": [
            dcc.Markdown("#### Building Flood Risk"),
            dcc.RadioItems(
                id='flood-risk-type-selector',
                options=[
                    {'label': 'Sea', 'value': 'Sea_risk'},
                    {'label': 'Rivers', 'value': 'Rivers_risk'},
                    {'label': 'Watercourses', 'value': 'Watercourses_Risk'},
                ],
                value='Sea_risk',
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            ),
            dcc.Graph(id="flood-risk-pie-chart", figure=initial_flood_risk_fig, style={'height': '80%'})
        ]
    }

    widgets = [
        crime_statistics_widget,
        network_statistics_widget,
        flood_risk_widget,
    ]
    return widgets
