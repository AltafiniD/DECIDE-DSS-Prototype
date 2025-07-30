# components/filter_panel.py

from dash import dcc, html
import pandas as pd
from config import NETWORK_METRICS_EXCLUDE, LAYER_CONFIG
from utils.geojson_loader import get_geojson_properties_keys

# THE FIX: This component no longer needs the large network_df.
def create_filter_panel(crime_df):
    """
    Creates the slide-down filter panel with dynamic network controls.
    """
    # --- Time Filter for Crimes ---
    crime_df['Month_dt'] = pd.to_datetime(crime_df['Month'], format='%Y-%m', errors='coerce')
    unique_months = sorted(crime_df['Month_dt'].dropna().unique())
    month_map = {i: month.strftime('%Y-%m') for i, month in enumerate(unique_months)}
    
    time_marks = {0: unique_months[0].strftime('%b %Y'), len(unique_months) - 1: unique_months[-1].strftime('%b %Y')} if unique_months else {}
    time_slider = dcc.RangeSlider(id='time-filter-slider', min=0, max=len(unique_months) - 1 if unique_months else 0, value=[0, len(unique_months) - 1 if unique_months else 0], marks=time_marks, step=1, tooltip={"placement": "bottom", "always_visible": False}, disabled=not bool(unique_months))

    # --- Crime Type Filter ---
    all_crime_types = sorted(crime_df['Crime type'].dropna().unique())
    crime_type_dropdown = dcc.Dropdown(id='crime-type-filter-dropdown', options=[{'label': crime, 'value': crime} for crime in all_crime_types], value=[], multi=True, placeholder="Filter by Crime Type (all shown by default)")

    # --- Dynamic Network Filter ---
    # THE FIX: Efficiently get network metric columns without loading the whole file.
    network_file_path = LAYER_CONFIG.get('network', {}).get('file_path')
    all_network_cols = get_geojson_properties_keys(network_file_path)
    # We can't check for numeric types this way, so we rely on the exclude list.
    # This assumes all non-excluded properties are numeric metrics.
    network_metrics = sorted([col for col in all_network_cols if col not in NETWORK_METRICS_EXCLUDE])
    
    network_metric_dropdown = dcc.Dropdown(
        id='network-metric-dropdown',
        options=[{'label': metric, 'value': metric} for metric in network_metrics],
        value='NAIN', # Default to NAIN
        clearable=False
    )
    # The range slider will be updated dynamically by a callback
    network_range_slider = dcc.RangeSlider(
        id='network-range-slider',
        min=0, max=1, value=[0, 1],
        step=0.01,
        tooltip={"placement": "bottom", "always_visible": True}
    )

    panel = html.Div(
        id="filter-slide-panel",
        className="filter-slide-panel filter-hidden",
        children=[
            html.Div(
                className="filter-inputs-wrapper",
                children=[
                    html.Div(className="filter-control", children=[html.Label("Time Range (Crimes)"), time_slider]),
                    html.Div(className="filter-control", children=[html.Label("Crime Types"), crime_type_dropdown]),
                    html.Div(className="filter-control", children=[
                        html.Label("Network Metric"),
                        network_metric_dropdown,
                        network_range_slider
                    ]),
                ]
            ),
            html.Button("Apply Filters", id="apply-filters-btn", n_clicks=0, className="apply-filters-button")
        ]
    )
    
    return panel, month_map
