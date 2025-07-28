# callbacks/widget_callbacks.py

import dash
from dash.dependencies import Input, Output
from dash import no_update
import pandas as pd
import json

from utils.geometry import is_point_in_polygon
from utils.colours import get_crime_colour_map
from components.crime_widget import create_crime_histogram_figure

def register_callbacks(app, crime_df, neighbourhoods_df):
    """
    Registers all widget-related callbacks.
    """
    plotly_colour_map, _ = get_crime_colour_map()

    # --- Debug Callback for the always-on selection panel ---
    @app.callback(
        Output("selection-info-display", "children"),
        Input("deck-gl", "clickInfo"),
    )
    def update_selection_display(click_info):
        """
        This callback acts as a debug tool. It displays the raw click
        information from the map in the selection panel.
        """
        if not click_info:
            return "#### Selection Debug\n\nClick an item on the map to see its raw data here."

        pretty_json = json.dumps(click_info, indent=2)
        return f"#### Last Click Data\n\n```json\n{pretty_json}\n```"

    # --- Callbacks for Graph and Map Interactivity ---
    @app.callback(
        Output("selected-neighbourhood-store", "data"),
        Input("deck-gl", "clickInfo"),
        prevent_initial_call=True
    )
    def update_selected_neighbourhood(click_info):
        if click_info and click_info.get('object') and click_info['object'].get('id') == 'neighbourhoods':
            return click_info['object']['properties']
        return None

    @app.callback(
        Output("selected-month-store", "data"),
        Input("crime-bar-chart", "clickData"),
        Input("clear-crime-filter-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def update_selected_month(chart_click, clear_clicks):
        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'clear-crime-filter-btn':
            return "clear"
        
        if chart_click:
            return chart_click['points'][0]['x']
        return no_update

    @app.callback(
        [
            Output("crime-bar-chart", "figure"),
            Output("crime-widget-title", "children")
        ],
        Input("selected-neighbourhood-store", "data"),
    )
    def update_crime_widget(selected_neighbourhood):
        widget_title = "#### Crime Statistics for Cardiff"
        chart_title = "Crimes per Month by Type"
        filtered_crime_df = crime_df

        if selected_neighbourhood:
            name = selected_neighbourhood.get('NAME')
            if name:
                widget_title = f"#### Crime Statistics for {name}"
                chart_title = f"Crimes in {name}"
                # This is the slow but stable filtering method
                poly_row = neighbourhoods_df[neighbourhoods_df['NAME'] == name]
                if not poly_row.empty:
                    polygon = poly_row.iloc[0]['contour']
                    mask = crime_df.apply(lambda row: is_point_in_polygon((row['Longitude'], row['Latitude']), polygon), axis=1)
                    filtered_crime_df = crime_df[mask]
        
        fig = create_crime_histogram_figure(filtered_crime_df, plotly_colour_map, title=chart_title)
        return fig, widget_title
