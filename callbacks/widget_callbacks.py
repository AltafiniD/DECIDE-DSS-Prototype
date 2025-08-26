# callbacks/widget_callbacks.py

import dash
from dash.dependencies import Input, Output, State
from dash import no_update, ctx
import pandas as pd
import json

from utils.geometry import is_point_in_polygon
from utils.colours import get_crime_colour_map
from components.crime_widget import create_crime_histogram_figure
from components.network_widget import create_network_histogram_figure
from components.flood_risk_widget import create_flood_risk_pie_chart

def register_callbacks(app, crime_df, neighbourhoods_df, network_df, buildings_df):
    """
    Registers all widget-related callbacks.
    """
    plotly_colour_map, _ = get_crime_colour_map()

    @app.callback(
        Output("selection-info-display", "children"),
        Input("deck-gl", "clickInfo"),
    )
    def update_selection_display(click_info):
        if not click_info:
            return "#### Selection Debug\n\nClick an item on the map to see its raw data here."
        pretty_json = json.dumps(click_info, indent=2)
        return f"#### Last Click Data\n\n```json\n{pretty_json}\n```"

    @app.callback(
        Output("selected-neighbourhood-store", "data"),
        Input("deck-gl", "clickInfo"),
        prevent_initial_call=True
    )
    def update_selected_neighbourhood(click_info):
        if click_info and click_info.get('object') and click_info['object'].get('id') == 'neighbourhoods':
            return click_info['object']['properties']
        return no_update

    @app.callback(
        Output('network-range-slider', 'value', allow_duplicate=True),
        Output('apply-filters-btn', 'n_clicks', allow_duplicate=True),
        Input('network-histogram-chart', 'clickData'),
        State('apply-filters-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_slider_from_histogram_click(chart_click, n_clicks):
        if not chart_click:
            return no_update, no_update
        new_range = chart_click['points'][0]['customdata'][:2]
        return new_range, n_clicks + 1

    @app.callback(
        Output('time-filter-slider', 'value'),
        Output('crime-type-filter-dropdown', 'value'),
        Output('apply-filters-btn', 'n_clicks'),
        Input('crime-bar-chart', 'clickData'),
        State('apply-filters-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_filters_from_graph(chart_click, n_clicks):
        if not chart_click:
            return no_update, no_update, no_update
        crime_type = chart_click['points'][0]['customdata'][0]
        return no_update, [crime_type], n_clicks + 1

    @app.callback(
        Output('time-filter-slider', 'value', allow_duplicate=True),
        Output('crime-type-filter-dropdown', 'value', allow_duplicate=True),
        Output('apply-filters-btn', 'n_clicks', allow_duplicate=True),
        Input('clear-crime-filter-btn', 'n_clicks'),
        State('month-map-store', 'data'),
        State('apply-filters-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_graph_filters(clear_clicks, month_map, n_clicks):
        if not clear_clicks:
            return no_update, no_update, no_update
        slider_reset_value = [0, len(month_map) - 1] if month_map else [0, 0]
        return slider_reset_value, [], n_clicks + 1

    @app.callback(
        [Output("crime-bar-chart", "figure"), Output("crime-widget-title", "children")],
        [Input("selected-neighbourhood-store", "data"), Input("apply-filters-btn", "n_clicks")],
        [State("time-filter-slider", "value"), State("crime-type-filter-dropdown", "value"), State("month-map-store", "data")]
    )
    def update_crime_widget(selected_neighbourhood, n_clicks, time_range, selected_crime_types, month_map):
        widget_title = "#### Crime Statistics for Cardiff"
        chart_title = "Crimes per Month by Type"
        filtered_crime_df = crime_df.copy()

        if time_range and month_map:
            start_month_str, end_month_str = month_map.get(str(time_range[0])), month_map.get(str(time_range[1]))
            if start_month_str and end_month_str:
                filtered_crime_df['Month_dt'] = pd.to_datetime(filtered_crime_df['Month'], errors='coerce')
                start_date, end_date = pd.to_datetime(start_month_str), pd.to_datetime(end_month_str)
                filtered_crime_df = filtered_crime_df[(filtered_crime_df['Month_dt'] >= start_date) & (filtered_crime_df['Month_dt'] <= end_date)]
        
        if selected_crime_types:
            filtered_crime_df = filtered_crime_df[filtered_crime_df['Crime type'].isin(selected_crime_types)]

        if selected_neighbourhood:
            name = selected_neighbourhood.get('NAME')
            if name:
                widget_title = f"#### Crime Statistics for {name}"
                chart_title = f"Crimes in {name}"
                poly_row = neighbourhoods_df[neighbourhoods_df['NAME'] == name]
                if not poly_row.empty:
                    polygon = poly_row.iloc[0]['contour']
                    mask = filtered_crime_df.apply(lambda row: is_point_in_polygon((row['Longitude'], row['Latitude']), polygon), axis=1)
                    filtered_crime_df = filtered_crime_df[mask]
        
        fig = create_crime_histogram_figure(filtered_crime_df, plotly_colour_map, title=chart_title)
        return fig, widget_title

    @app.callback(
        Output("network-histogram-chart", "figure"),
        Input("apply-filters-btn", "n_clicks"),
        [State("network-metric-dropdown", "value"), State("network-range-slider", "value")],
        prevent_initial_call=True
    )
    def update_network_widget(n_clicks, network_metric, network_range):
        if not n_clicks or not network_metric or not network_range:
            return no_update

        df = network_df.copy()
        df[network_metric] = pd.to_numeric(df[network_metric], errors='coerce')
        mask = (df[network_metric] >= network_range[0]) & (df[network_metric] <= network_range[1])
        filtered_series = df.loc[mask, network_metric].dropna()

        fig = create_network_histogram_figure(filtered_series, network_metric)
        return fig

    @app.callback(
        Output("flood-risk-pie-chart", "figure"),
        Input("flood-risk-type-selector", "value")
    )
    def update_flood_risk_widget(risk_type):
        """
        Updates the flood risk pie chart based on the selected risk type.
        """
        if not risk_type:
            return no_update
        
        # --- MODIFIED: Set title to an empty string to remove it ---
        title = ""
        fig = create_flood_risk_pie_chart(buildings_df, risk_type, title=title)
        return fig
