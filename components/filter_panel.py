# components/filter_panel.py

from dash import dcc, html
import pandas as pd
from config import NETWORK_METRICS_EXCLUDE, FLOOD_LAYER_CONFIG, BUILDING_COLOR_CONFIG

def create_filter_panel(crime_df, network_df, deprivation_df, buildings_df, land_use_df, neighbourhoods_df):
    """
    Creates the slide-down filter panel with controls grouped into styled boxes.
    """
    # --- Component creation logic ---
    crime_df['Month_dt'] = pd.to_datetime(crime_df['Month'], format='%Y-%m', errors='coerce')
    unique_months = sorted(crime_df['Month_dt'].dropna().unique())
    month_map = {i: month.strftime('%Y-%m') for i, month in enumerate(unique_months)}
    time_marks = {0: unique_months[0].strftime('%b %Y'), len(unique_months) - 1: unique_months[-1].strftime('%b %Y')} if unique_months else {}
    time_slider = dcc.RangeSlider(id='time-filter-slider', min=0, max=len(unique_months) - 1 if unique_months else 0, value=[0, len(unique_months) - 1 if unique_months else 0], marks=time_marks, step=1, tooltip={"placement": "bottom", "always_visible": False}, disabled=not bool(unique_months))
    
    all_crime_types = sorted(crime_df['Crime type'].dropna().unique())
    crime_type_dropdown = dcc.Dropdown(id='crime-type-filter-dropdown', options=[{'label': crime, 'value': crime} for crime in all_crime_types], value=[], multi=True, placeholder="Filter by Crime Type")
    
    numeric_cols = network_df.select_dtypes(include='number').columns.tolist()
    network_metrics = sorted([col for col in numeric_cols if col not in NETWORK_METRICS_EXCLUDE])
    network_metric_dropdown = dcc.Dropdown(id='network-metric-dropdown', options=[{'label': metric, 'value': metric} for metric in network_metrics], value='NAIN', clearable=False)
    network_range_slider = dcc.RangeSlider(id='network-range-slider', min=0, max=1, value=[0, 1], step=0.01, tooltip={"placement": "bottom", "always_visible": True})

    deprivation_options = [
        {'label': 'Not Deprived', 'value': 'Household is not deprived in any dimension'},
        {'label': '1 Dimension', 'value': 'Household is deprived in one dimension'},
        {'label': '2 Dimensions', 'value': 'Household is deprived in two dimensions'},
        {'label': '3 Dimensions', 'value': 'Household is deprived in three dimensions'},
        {'label': '4+ Dimensions', 'value': '4+'},
    ]
    deprivation_dropdown = dcc.Dropdown(
        id='deprivation-category-dropdown',
        options=deprivation_options,
        value='Household is deprived in one dimension',
        clearable=False
    )
    
    all_land_use_types = sorted(land_use_df['landuse_text'].dropna().unique())
    land_use_type_dropdown = dcc.Dropdown(id='land-use-type-dropdown', options=[{'label': lu_type, 'value': lu_type} for lu_type in all_land_use_types], value=[], multi=True, placeholder="Filter by Land Use Type")

    flood_options = [{'label': config['label'], 'value': config['id']} for config in FLOOD_LAYER_CONFIG.values()]
    flood_risk_selector = dcc.Dropdown(id='flood-risk-selector', options=flood_options, value=['flood_sea'], multi=True, placeholder="Select Flood Risk Layers")
    
    building_color_options = [{'label': config['label'], 'value': key} for key, config in BUILDING_COLOR_CONFIG.items()]
    building_color_selector = dcc.Dropdown(id='building-color-selector', options=building_color_options, value='none', clearable=False)
    
    # --- NEW: Neighbourhood Filter ---
    all_neighbourhoods = sorted(neighbourhoods_df['NAME'].dropna().unique()) if neighbourhoods_df is not None and not neighbourhoods_df.empty else []
    neighbourhood_dropdown = dcc.Dropdown(
        id='neighbourhood-filter-dropdown',
        options=[{'label': name, 'value': name} for name in all_neighbourhoods],
        value=all_neighbourhoods, 
        multi=True, 
        placeholder="Filter by Neighbourhood"
    )

    panel = html.Div(
        id="filter-slide-panel",
        className="filter-slide-panel filter-hidden",
        children=[
            html.Div(
                className="filter-inputs-wrapper",
                children=[
                    # --- Column 1 ---
                    html.Div(
                        className="filter-column",
                        children=[
                            # --- NEW: Neighbourhood Filter Widget ---
                            html.Div(className="control-widget", children=[
                                html.H3("Neighbourhood Filters", style={'marginTop': 0}),
                                html.Label("Select Neighbourhoods"),
                                neighbourhood_dropdown
                            ]),
                            html.Div(className="control-widget", children=[
                                html.H3("Crime Filters", style={'marginTop': 0}),
                                html.Label("Crime Types"), crime_type_dropdown,
                                html.Label("Time Range", style={'marginTop': '15px'}), time_slider
                            ]),
                            html.Div(className="control-widget", children=[
                                html.H3("Building Filters", style={'marginTop': 0}),
                                html.Label("Building Coloring"), building_color_selector
                            ]),
                        ]
                    ),
                    # --- Column 2 ---
                    html.Div(
                        className="filter-column",
                        children=[
                            html.Div(className="control-widget", children=[
                                html.H3("Network Analysis", style={'marginTop': 0}),
                                html.Label("Network Metric"), network_metric_dropdown,
                                network_range_slider
                            ]),
                            html.Div(className="control-widget", children=[
                                html.H3("Social Filters", style={'marginTop': 0}),
                                html.Label("Deprivation Category"), deprivation_dropdown
                            ]),
                            html.Div(className="control-widget", children=[
                                html.H3("Environmental & Land Use", style={'marginTop': 0}),
                                html.Label("Flood Risk Layer"), flood_risk_selector,
                                html.Label("Land Use Type", style={'marginTop': '15px'}), land_use_type_dropdown
                            ]),
                        ]
                    ),
                ]
            ),
            html.Button("Apply Filters", id="apply-filters-btn", n_clicks=0, className="apply-filters-button")
        ]
    )
    
    return panel, month_map

