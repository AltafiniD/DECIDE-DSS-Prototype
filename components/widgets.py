# components/widgets.py
from dash import dcc, html
import pandas as pd
from .crime_widget import create_crime_histogram_figure
from .network_widget import create_network_histogram_figure
from .flood_risk_widget import create_flood_risk_pie_chart
from .land_use_widget import create_land_use_donut_chart
from .jenks_histogram_widget import create_jenks_histogram_figure
from .buildings_at_risk_widget import create_buildings_at_risk_widget
from .deprivation_widget import create_deprivation_pie_chart # --- NEW: Import the deprivation chart function ---

def get_widgets(dataframes, color_map):
    """
    Defines a list of all widgets to be displayed in the slide-over panel.
    """
    crime_df = dataframes.get('crime_points', pd.DataFrame())
    network_df = dataframes.get('network', pd.DataFrame())
    buildings_df = dataframes.get('buildings', pd.DataFrame())
    land_use_df = dataframes.get('land_use', pd.DataFrame())
    deprivation_df = dataframes.get('deprivation', pd.DataFrame()) # --- NEW: Get the deprivation dataframe ---
    
    initial_crime_fig = create_crime_histogram_figure(crime_df, color_map)
    
    initial_metric = 'NAIN' if 'NAIN' in network_df.columns else None
    initial_metric_series = network_df[initial_metric] if initial_metric and not network_df.empty else pd.Series()
    initial_network_fig = create_network_histogram_figure(initial_metric_series, initial_metric)
    initial_jenks_fig = create_jenks_histogram_figure(initial_metric_series, initial_metric)

    initial_flood_risk_fig = create_flood_risk_pie_chart(buildings_df, 'Sea_risk', title="")
    
    initial_land_use_fig = create_land_use_donut_chart(land_use_df, title="Cardiff Land Use")

    buildings_at_risk_content = create_buildings_at_risk_widget(buildings_df)

    # --- NEW: Create the initial figure for the deprivation widget ---
    initial_deprivation_fig = create_deprivation_pie_chart(deprivation_df, title="Cardiff Deprivation Overview")

    # --- NEW: Define the deprivation widget ---
    deprivation_widget = {
        "size": (1, 2),
        "content": [
            dcc.Markdown(id="deprivation-widget-title", children="#### Household Deprivation"),
            dcc.Graph(id="deprivation-pie-chart", figure=initial_deprivation_fig, style={'height': '85%'})
        ]
    }

    buildings_at_risk_widget = {
        "size": (1, 1),
        "content": buildings_at_risk_content
    }

    crime_statistics_widget = {
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
        "size": (2, 2),
        "content": [
            dcc.Markdown("#### Network Metric Distribution (Deciles)"),
            dcc.Graph(id="network-histogram-chart", figure=initial_network_fig, style={'height': '85%'})
        ]
    }

    flood_risk_widget = {
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

    land_use_widget = {
        "size": (2, 2),
        "content": [
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'},
                children=[
                    dcc.Markdown(id="land-use-widget-title", children="#### Land Use"),
                    html.Button("Clear Filter", id="clear-land-use-filter-btn", n_clicks=0, style={'fontSize': '12px'})
                ]
            ),
            dcc.Graph(id="land-use-donut-chart", figure=initial_land_use_fig, style={'height': '80%'})
        ]
    }

    jenks_widget = {
        "size": (2, 2),
        "content": [
            dcc.Markdown("#### Network Metric Distribution (Jenks Breaks)"),
            dcc.Graph(id="jenks-histogram-chart", figure=initial_jenks_fig, style={'height': '85%'})
        ]
    }

    widgets = [
        crime_statistics_widget,
        network_statistics_widget,
        jenks_widget,
        deprivation_widget, # --- NEW: Add the widget to the list ---
        buildings_at_risk_widget,
        flood_risk_widget,
        land_use_widget,
    ]
    return widgets

