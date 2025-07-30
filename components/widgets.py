# components/widgets.py
from dash import dcc, html
import pandas as pd
from .crime_widget import create_crime_histogram_figure
# --- NEW: Import the network widget creator ---
from .network_widget import create_network_histogram_figure

def get_widgets(dataframes, color_map):
    """
    Defines a list of all widgets to be displayed in the slide-over panel.
    """
    crime_df = dataframes.get('crime_points', pd.DataFrame())
    network_df = dataframes.get('network', pd.DataFrame())
    
    initial_crime_fig = create_crime_histogram_figure(crime_df, color_map)
    
    # --- NEW: Create an initial (empty) figure for the network widget ---
    initial_metric = 'NAIN' if 'NAIN' in network_df.columns else None
    initial_metric_series = network_df[initial_metric] if initial_metric and not network_df.empty else pd.Series()
    initial_network_fig = create_network_histogram_figure(initial_metric_series, initial_metric)

    crime_statistics_widget = {
        "size": (3, 3),
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

    # --- NEW: Define the network statistics widget ---
    network_statistics_widget = {
        "size": (3, 2), # A bit shorter than the crime one
        "content": [
            dcc.Graph(id="network-histogram-chart", figure=initial_network_fig, style={'height': '100%'})
        ]
    }

    widgets = [
        crime_statistics_widget,
        network_statistics_widget, # Add the new widget to the list
    ]
    return widgets
