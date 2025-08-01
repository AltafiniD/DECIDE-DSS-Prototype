# components/filter_panel.py

from dash import dcc, html
import pandas as pd
# --- UPDATED: Import the new flood config ---
from config import NETWORK_METRICS_EXCLUDE, FLOOD_LAYER_CONFIG

def create_filter_panel(crime_df, network_df, deprivation_df):
    """
    Creates the slide-down filter panel with all dynamic controls.
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
    numeric_cols = network_df.select_dtypes(include='number').columns.tolist()
    network_metrics = sorted([col for col in numeric_cols if col not in NETWORK_METRICS_EXCLUDE])
    network_metric_dropdown = dcc.Dropdown(id='network-metric-dropdown', options=[{'label': metric, 'value': metric} for metric in network_metrics], value='NAIN', clearable=False)
    network_range_slider = dcc.RangeSlider(id='network-range-slider', min=0, max=1, value=[0, 1], step=0.01, tooltip={"placement": "bottom", "always_visible": True})

    # --- Deprivation Category Filter ---
    deprivation_category_col = "Household deprivation (6 categories)"
    deprivation_options = []
    if deprivation_category_col in deprivation_df.columns:
        categories = sorted(deprivation_df[deprivation_category_col].dropna().unique())
        deprivation_options = [{'label': 'All Categories', 'value': 'all'}] + [{'label': cat, 'value': cat} for cat in categories]
    deprivation_dropdown = dcc.Dropdown(id='deprivation-category-dropdown', options=deprivation_options, value='all', placeholder="Filter by Deprivation Category", clearable=False)

    # --- Flood Risk Layer Selector ---
    flood_options = [
        {'label': config['label'], 'value': config['id']} for config in FLOOD_LAYER_CONFIG.values()
    ]
    flood_risk_selector = dcc.Dropdown(
        id='flood-risk-selector',
        options=flood_options,
        value=['flood_sea'], # --- UPDATED: Default to "Risk from Sea" ---
        multi=True,
        placeholder="Select Flood Risk Layers"
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
                    html.Div(className="filter-control", children=[html.Label("Network Metric"), network_metric_dropdown, network_range_slider]),
                    html.Div(className="filter-control", children=[html.Label("Deprivation Category"), deprivation_dropdown]),
                    html.Div(className="filter-control", children=[html.Label("Flood Risk Layer"), flood_risk_selector]),
                ]
            ),
            html.Button("Apply Filters", id="apply-filters-btn", n_clicks=0, className="apply-filters-button")
        ]
    )
    
    return panel, month_map
