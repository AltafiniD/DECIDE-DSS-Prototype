# components/filter_panel.py

from dash import dcc, html
import pandas as pd
from config import NETWORK_METRICS_EXCLUDE, FLOOD_LAYER_CONFIG, BUILDING_COLOR_CONFIG

def create_filter_panel(crime_df, network_df, deprivation_df, buildings_df, land_use_df, neighbourhoods_df, stop_and_search_df):
    """
    Creates the slide-down filter panel with controls grouped into styled boxes.
    Handles None or empty dataframes gracefully.
    """
    
    # --- Crime Data Components ---
    if crime_df is not None and not crime_df.empty and 'Month' in crime_df.columns:
        crime_df['Month_dt'] = pd.to_datetime(crime_df['Month'], format='%Y-%m', errors='coerce')
        unique_crime_months = sorted(crime_df['Month_dt'].dropna().unique())
        crime_month_map = {i: month.strftime('%Y-%m') for i, month in enumerate(unique_crime_months)}
        crime_time_marks = {0: unique_crime_months[0].strftime('%b %Y'), len(unique_crime_months) - 1: unique_crime_months[-1].strftime('%b %Y')} if unique_crime_months else {}
        all_crime_types = sorted(crime_df['Crime type'].dropna().unique()) if 'Crime type' in crime_df.columns else []
    else:
        unique_crime_months = []
        crime_month_map = {}
        crime_time_marks = {}
        all_crime_types = []
    
    crime_time_slider = dcc.RangeSlider(
        id='time-filter-slider', 
        min=0, 
        max=len(unique_crime_months) - 1 if unique_crime_months else 0, 
        value=[0, len(unique_crime_months) - 1 if unique_crime_months else 0], 
        marks=crime_time_marks, 
        step=1, 
        tooltip={"placement": "bottom", "always_visible": False}, 
        disabled=not bool(unique_crime_months)
    )
    
    crime_type_dropdown = dcc.Dropdown(
        id='crime-type-filter-dropdown', 
        options=[{'label': crime, 'value': crime} for crime in all_crime_types], 
        value=[], 
        multi=True, 
        placeholder="Filter by Crime Type"
    )
    
    # --- Stop & Search Data Components ---
    if stop_and_search_df is not None and not stop_and_search_df.empty and 'Date' in stop_and_search_df.columns:
        stop_and_search_df['Month_dt'] = pd.to_datetime(stop_and_search_df['Date'], errors='coerce').dt.to_period('M').dt.to_timestamp()
        unique_sas_months = sorted(stop_and_search_df['Month_dt'].dropna().unique())
        sas_month_map = {i: month.strftime('%Y-%m') for i, month in enumerate(unique_sas_months)}
        sas_time_marks = {0: unique_sas_months[0].strftime('%b %Y'), len(unique_sas_months) - 1: unique_sas_months[-1].strftime('%b %Y')} if unique_sas_months else {}
        all_sas_objects = sorted(stop_and_search_df['Object of search'].dropna().unique()) if 'Object of search' in stop_and_search_df.columns else []
    else:
        unique_sas_months = []
        sas_month_map = {}
        sas_time_marks = {}
        all_sas_objects = []
    
    sas_time_slider = dcc.RangeSlider(
        id='sas-time-filter-slider', 
        min=0, 
        max=len(unique_sas_months) - 1 if unique_sas_months else 0, 
        value=[0, len(unique_sas_months) - 1 if unique_sas_months else 0], 
        marks=sas_time_marks, 
        step=1, 
        tooltip={"placement": "bottom", "always_visible": False}, 
        disabled=not bool(unique_sas_months)
    )
    
    sas_object_dropdown = dcc.Dropdown(
        id='sas-object-filter-dropdown', 
        options=[{'label': obj, 'value': obj} for obj in all_sas_objects], 
        value=[], 
        multi=True, 
        placeholder="Filter by Object of Search"
    )

    if network_df is not None and not network_df.empty:
        numeric_cols = network_df.select_dtypes(include='number').columns.tolist()
        network_metrics = sorted([col for col in numeric_cols if col not in NETWORK_METRICS_EXCLUDE])
    else:
        network_metrics = []
    
    network_metric_dropdown = dcc.Dropdown(
        id='network-metric-dropdown', 
        options=[{'label': metric, 'value': metric} for metric in network_metrics], 
        # MODIFIED: Changed default value to 'NAIN_rivers_risk' with fallbacks
        value='NACH_rivers_risk' if 'NACH_rivers_risk' in network_metrics else ('NAIN' if 'NAIN' in network_metrics else (network_metrics[0] if network_metrics else None)), 
        clearable=False,
        disabled=not bool(network_metrics)
    )
    
    network_range_slider = dcc.RangeSlider(
        id='network-range-slider', 
        min=0, 
        max=1, 
        value=[0, 1], 
        step=0.01, 
        tooltip={"placement": "bottom", "always_visible": True}
    )

    # --- Deprivation Components ---
    deprivation_values = [
        'Household is not deprived in any dimension',
        'Household is deprived in one dimension',
        'Household is deprived in two dimensions',
        'Household is deprived in three dimensions',
        '4+'
    ]
    deprivation_options = [
        {'label': 'Not Deprived in any Dimension', 'value': deprivation_values[0]},
        {'label': 'Deprived in One Dimension', 'value': deprivation_values[1]},
        {'label': 'Deprived in Two Dimensions', 'value': deprivation_values[2]},
        {'label': 'Deprived in Three Dimensions', 'value': deprivation_values[3]},
        {'label': 'Deprived in all Dimensions', 'value': deprivation_values[4]},
    ]
    
    deprivation_dropdown = dcc.Dropdown(
        id='deprivation-category-dropdown',
        options=deprivation_options,
        value=deprivation_values[0],
        clearable=False,
        style={'width': '300px', 'minWidth': '160px'},
        maxHeight=64,
        optionHeight=32
    )

    # --- Land Use Components ---
    if land_use_df is not None and not land_use_df.empty and 'landuse_text' in land_use_df.columns:
        all_land_use_types = sorted(land_use_df['landuse_text'].dropna().unique())
    else:
        all_land_use_types = []
    
    land_use_type_dropdown = dcc.Dropdown(
        id='land-use-type-dropdown', 
        options=[{'label': lu_type, 'value': lu_type} for lu_type in all_land_use_types], 
        value=[], 
        multi=True, 
        placeholder="Filter by Land Use Type"
    )

    # --- Flood and Building Components ---
    flood_options = [{'label': config['label'], 'value': config['id']} for config in FLOOD_LAYER_CONFIG.values()]
    flood_risk_selector = dcc.Dropdown(
        id='flood-risk-selector', 
        options=flood_options, 
        value=['flood_rivers_high', 'flood_rivers_medium', 'flood_rivers_low'], # Default selected values, see config.py [FLOOD_LAYER_CONFIG] for correct namings
        multi=True, 
        placeholder="Select Flood Risk Layers"
    )
    
    building_color_options = [{'label': config['label'], 'value': key} for key, config in BUILDING_COLOR_CONFIG.items()]
    building_color_selector = dcc.Dropdown(
        id='building-color-selector', 
        options=building_color_options, 
        value='none', 
        clearable=False
    )
    
    # --- Neighbourhood Components ---
    if neighbourhoods_df is not None and not neighbourhoods_df.empty and 'NAME' in neighbourhoods_df.columns:
        all_neighbourhoods = sorted(neighbourhoods_df['NAME'].dropna().unique())
    else:
        all_neighbourhoods = []
    
    neighbourhood_dropdown = dcc.Dropdown(
        id='neighbourhood-filter-dropdown', 
        options=[{'label': name, 'value': name} for name in all_neighbourhoods], 
        value=[], 
        multi=True, 
        placeholder="Filter by Neighbourhood (all shown by default)"
    )

    # --- Build Panel ---
    panel = html.Div(
        id="filter-slide-panel",
        className="filter-slide-panel filter-hidden",
        children=[
            html.Div(
                className="filter-inputs-wrapper",
                children=[
                    html.Div(
                        className="filter-column",
                        children=[
                            html.Div(className="control-widget", children=[
                                html.H3("Neighbourhood Filters", style={'marginTop': 0}),
                                neighbourhood_dropdown
                            ]),
                            html.Div(className="control-widget", children=[
                                html.H3("Crime Filters", style={'marginTop': 0}),
                                crime_type_dropdown,
                                html.Label("Time Range", style={'marginTop': '15px'}), crime_time_slider
                            ]),
                            html.Div(className="control-widget", children=[
                                html.H3("Policing Filters (Stop & Search)", style={'marginTop': 0}),
                                sas_object_dropdown,
                                html.Label("Time Range", style={'marginTop': '15px'}), sas_time_slider
                            ]),
                        ]
                    ),
                    html.Div(
                        className="filter-column",
                        children=[
                            html.Div(className="control-widget", children=[
                                html.H3("Building & Environmental", style={'marginTop': 0}),
                                html.Label("Buildings at Risk"), building_color_selector,
                                html.Label("Flood Hazard Layer", style={'marginTop': '15px'}), flood_risk_selector,
                                html.Label("Land Use Type", style={'marginTop': '15px'}), land_use_type_dropdown
                            ]),
                            html.Div(className="control-widget", children=[
                                html.H3("Network Analysis", style={'marginTop': 0}),
                                network_metric_dropdown,
                                network_range_slider
                            ]),
                            html.Div(className="control-widget", children=[
                                html.H3("Deprivation Category", style={'marginTop': 0}),
                                deprivation_dropdown
                            ]),
                        ]
                    ),
                ]
            ),
            html.Button("Apply Filters", id="apply-filters-btn", n_clicks=0, className="apply-filters-button")
        ]
    )
    
    return panel, crime_month_map, sas_month_map
