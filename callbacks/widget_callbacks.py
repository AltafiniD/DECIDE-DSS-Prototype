# callbacks/widget_callbacks.py

import dash
from dash.dependencies import Input, Output, State
from dash import no_update, ctx, html, dcc
import pandas as pd
import json

# --- MODIFIED: Import LAYER_CONFIG to ensure correct layer order ---
from config import LAYER_CONFIG
from utils.geometry import is_point_in_polygon
from utils.colours import get_crime_colour_map
from components.crime_widget import create_crime_histogram_figure
from components.network_widget import create_network_histogram_figure
from components.flood_risk_widget import create_flood_risk_pie_chart
from components.land_use_widget import create_land_use_donut_chart
from components.jenks_histogram_widget import create_jenks_histogram_figure
from components.buildings_at_risk_widget import create_buildings_at_risk_widget
from components.deprivation_widget import create_deprivation_bar_chart
from components.population_widget import create_population_density_histogram
from shapely.geometry import Point, Polygon

def register_callbacks(app, crime_df, neighbourhoods_df, network_df, buildings_df, land_use_df, deprivation_df, population_df):
    """
    Registers all widget-related callbacks.
    """
    plotly_colour_map, _ = get_crime_colour_map()

    @app.callback(
        Output("widget-grid-container", "children"),
        Input("map-update-trigger-store", "data"),
        prevent_initial_call=True
    )
    def update_widget_panel(trigger_data):
        if not trigger_data:
            return no_update

        crime_viz_selection = trigger_data.get("crime_viz")
        # --- FIXED: Generate the layer ID list dynamically to match the input order ---
        all_toggle_ids = [k for k, v in LAYER_CONFIG.items() if not k.startswith('crime_')]
        toggles_dict = dict(zip(all_toggle_ids, trigger_data.get("toggles", [])))

        widgets_data = []

        if crime_viz_selection:
            initial_crime_fig = create_crime_histogram_figure(crime_df, plotly_colour_map)
            widgets_data.append({
                "size": (2, 3), "content": [
                    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
                        dcc.Markdown(id="crime-widget-title", children="#### Crime Statistics for Cardiff"),
                        html.Button("Clear Selection", id="clear-crime-filter-btn", n_clicks=0, style={'fontSize': '12px'})]),
                    dcc.Graph(id="crime-bar-chart", figure=initial_crime_fig, style={'height': '85%'})]})

        if toggles_dict.get('network'):
            initial_metric = 'NAIN' if 'NAIN' in network_df.columns else None
            series = network_df[initial_metric] if initial_metric and not network_df.empty else pd.Series()
            initial_network_fig = create_network_histogram_figure(series, initial_metric)
            initial_jenks_fig = create_jenks_histogram_figure(series, initial_metric)
            widgets_data.append({"size": (2, 2), "content": [dcc.Markdown("#### Network Metric Distribution (Deciles)"), dcc.Graph(id="network-histogram-chart", figure=initial_network_fig, style={'height': '85%'})]})
            widgets_data.append({"size": (2, 2), "content": [dcc.Markdown("#### Network Metric Distribution (Jenks Breaks)"), dcc.Graph(id="jenks-histogram-chart", figure=initial_jenks_fig, style={'height': '85%'})]})

        if toggles_dict.get('buildings'):
            initial_flood_fig = create_flood_risk_pie_chart(buildings_df, 'Sea_risk', title="")
            buildings_at_risk_content = create_buildings_at_risk_widget(buildings_df)
            widgets_data.append({"size": (1, 1), "content": buildings_at_risk_content})
            widgets_data.append({"size": (1, 2), "content": [dcc.Markdown("#### Building Flood Risk"), dcc.RadioItems(id='flood-risk-type-selector', options=[{'label': 'Sea', 'value': 'Sea_risk'}, {'label': 'Rivers', 'value': 'Rivers_risk'}, {'label': 'Watercourses', 'value': 'Watercourses_Risk'}], value='Sea_risk', labelStyle={'display': 'inline-block', 'margin-right': '10px'}), dcc.Graph(id="flood-risk-pie-chart", figure=initial_flood_fig, style={'height': '80%'})]})

        if toggles_dict.get('land_use'):
            initial_land_use_fig = create_land_use_donut_chart(land_use_df, title="Cardiff Land Use")
            widgets_data.append({"size": (2, 2), "content": [html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[dcc.Markdown(id="land-use-widget-title", children="#### Land Use"), html.Button("Clear Filter", id="clear-land-use-filter-btn", n_clicks=0, style={'fontSize': '12px'})]), dcc.Graph(id="land-use-donut-chart", figure=initial_land_use_fig, style={'height': '80%'})]})

        if toggles_dict.get('deprivation'):
            initial_deprivation_fig = create_deprivation_bar_chart(deprivation_df)
            widgets_data.append({"size": (2, 2), "content": [dcc.Markdown(id="deprivation-widget-title", children="#### Household Deprivation by Percentile"), dcc.Graph(id="deprivation-bar-chart", figure=initial_deprivation_fig, style={'height': 'calc(100% - 30px)'})]})

        if toggles_dict.get('population'):
            initial_population_fig = create_population_density_histogram(population_df)
            widgets_data.append({
                "size": (2, 2),
                "content": [
                    dcc.Markdown("#### Population Density (Jenks Breaks)"),
                    dcc.Graph(id="population-density-chart", figure=initial_population_fig, style={'height': '85%'})
                ]
            })

        if not widgets_data:
            return []

        widgets_data.sort(key=lambda w: w['size'][0] * w['size'][1], reverse=True)
        grid_width, occupied_cells, placed_widgets, row = 2, set(), [], 0

        while widgets_data:
            col = 0
            while col < grid_width:
                if (row, col) not in occupied_cells:
                    widget_to_place = None
                    for i, widget in enumerate(widgets_data):
                        w_width, w_height = int(widget['size'][0]), int(widget['size'][1])
                        if col + w_width <= grid_width and all((row + r, col + c) not in occupied_cells for r in range(w_height) for c in range(w_width)):
                            widget_to_place = widgets_data.pop(i)
                            break
                    if widget_to_place:
                        w_width, w_height = widget_to_place['size']
                        placed_widgets.append(html.Div(className="widget", style={'--grid-col-start': col + 1, '--grid-row-start': row + 1, '--grid-col-span': w_width, '--grid-row-span': w_height}, children=widget_to_place['content']))
                        for r_offset in range(int(w_height)):
                            for c_offset in range(int(w_width)):
                                occupied_cells.add((row + r_offset, col + c_offset))
                col += 1
            row += 1

        return placed_widgets

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

        if not chart_click['points'][0].get('customdata'):
            return no_update, no_update

        new_range = chart_click['points'][0]['customdata'][:2]
        return new_range, (n_clicks or 0) + 1

    @app.callback(
        Output('time-filter-slider', 'value'),
        Output('crime-type-filter-dropdown', 'value'),
        Output('apply-filters-btn', 'n_clicks', allow_duplicate=True),
        Input('crime-bar-chart', 'clickData'),
        State('apply-filters-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_filters_from_graph(chart_click, n_clicks):
        if not chart_click:
            return no_update, no_update, no_update
        crime_type = chart_click['points'][0]['customdata'][0]
        return no_update, [crime_type], (n_clicks or 0) + 1

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
        return slider_reset_value, [], (n_clicks or 0) + 1

    @app.callback(
        [Output("crime-bar-chart", "figure"), Output("crime-widget-title", "children")],
        [Input("selected-neighbourhood-store", "data"), Input("apply-filters-btn", "n_clicks")],
        [State("time-filter-slider", "value"), State("crime-type-filter-dropdown", "value"), State("month-map-store", "data")]
    )
    def update_crime_widget(selected_neighbourhood, n_clicks, time_range, selected_crime_types, month_map):
        widget_title = "#### Crime Statistics for Cardiff"
        chart_title = "Crimes per Month by Type"

        df_to_filter = crime_df.copy()

        if selected_neighbourhood:
            name = selected_neighbourhood.get('NAME')
            if name:
                widget_title = f"#### Crime Statistics for {name}"
                chart_title = f"Crimes in {name}"
                poly_row = neighbourhoods_df[neighbourhoods_df['NAME'] == name]
                if not poly_row.empty:
                    polygon = poly_row.iloc[0]['contour']
                    mask = df_to_filter.apply(lambda row: is_point_in_polygon((row['Longitude'], row['Latitude']), polygon), axis=1)
                    df_to_filter = df_to_filter[mask]

        if time_range and month_map:
            start_month_str, end_month_str = month_map.get(str(time_range[0])), month_map.get(str(time_range[1]))
            if start_month_str and end_month_str:
                df_to_filter['Month_dt'] = pd.to_datetime(df_to_filter['Month'], errors='coerce')
                start_date, end_date = pd.to_datetime(start_month_str), pd.to_datetime(end_month_str)
                df_to_filter = df_to_filter[(df_to_filter['Month_dt'] >= start_date) & (df_to_filter['Month_dt'] <= end_date)]

        if selected_crime_types:
            df_to_filter = df_to_filter[df_to_filter['Crime type'].isin(selected_crime_types)]

        fig = create_crime_histogram_figure(df_to_filter, plotly_colour_map, title=chart_title)
        return fig, widget_title

    @app.callback(
        [Output("network-histogram-chart", "figure"), Output("jenks-histogram-chart", "figure")],
        Input("apply-filters-btn", "n_clicks"),
        [State("network-metric-dropdown", "value"), State("network-range-slider", "value")],
    )
    def update_network_widgets(n_clicks, network_metric, network_range):
        if not network_metric or not network_range:
            return no_update, no_update

        df = network_df.copy()
        df[network_metric] = pd.to_numeric(df[network_metric], errors='coerce')
        mask = (df[network_metric] >= network_range[0]) & (df[network_metric] <= network_range[1])
        filtered_series = df.loc[mask, network_metric].dropna()

        decile_fig = create_network_histogram_figure(filtered_series, network_metric)
        jenks_fig = create_jenks_histogram_figure(filtered_series, network_metric)
        return decile_fig, jenks_fig

    @app.callback(
        Output("flood-risk-pie-chart", "figure"),
        Input("flood-risk-type-selector", "value")
    )
    def update_flood_risk_widget(risk_type):
        if not risk_type:
            return no_update

        title = ""
        fig = create_flood_risk_pie_chart(buildings_df, risk_type, title=title)
        return fig

    @app.callback(
        Output('land-use-type-dropdown', 'value'),
        Output('apply-filters-btn', 'n_clicks', allow_duplicate=True),
        Input('land-use-donut-chart', 'clickData'),
        State('apply-filters-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_filter_from_land_use_click(chart_click, n_clicks):
        if not chart_click or not chart_click['points'][0].get('customdata'):
            return no_update, no_update

        land_use_type = chart_click['points'][0]['customdata'][0]

        if land_use_type == 'Other':
            return [], no_update

        return [land_use_type], (n_clicks or 0) + 1

    @app.callback(
        Output('land-use-type-dropdown', 'value', allow_duplicate=True),
        Output('apply-filters-btn', 'n_clicks', allow_duplicate=True),
        Input('clear-land-use-filter-btn', 'n_clicks'),
        State('apply-filters-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_land_use_filter(clear_clicks, n_clicks):
        if not clear_clicks:
            return no_update, no_update
        return [], (n_clicks or 0) + 1

    @app.callback(
        [Output("land-use-donut-chart", "figure"), Output("land-use-widget-title", "children")],
        [Input("selected-neighbourhood-store", "data"), Input("apply-filters-btn", "n_clicks")],
        [State("land-use-type-dropdown", "value")]
    )
    def update_land_use_widget(selected_neighbourhood, n_clicks, selected_land_use):
        widget_title = "#### Land Use for Cardiff"
        chart_title = "Land Use Distribution"

        df_to_filter = land_use_df.copy()

        if selected_neighbourhood:
            name = selected_neighbourhood.get('NAME')
            if name:
                widget_title = f"#### Land Use for {name}"
                chart_title = f"Land Use in {name}"
                poly_row = neighbourhoods_df[neighbourhoods_df['NAME'] == name]
                if not poly_row.empty:
                    neighbourhood_polygon = Polygon(poly_row.iloc[0]['contour'])

                    def is_land_use_in_neighbourhood(row):
                        land_use_poly = Polygon(row['contour'])
                        return neighbourhood_polygon.contains(land_use_poly.representative_point())

                    mask = df_to_filter.apply(is_land_use_in_neighbourhood, axis=1)
                    df_to_filter = df_to_filter[mask]

        if selected_land_use:
            df_to_filter = df_to_filter[df_to_filter['landuse_text'].isin(selected_land_use)]

        fig = create_land_use_donut_chart(df_to_filter, title=chart_title)
        return fig, widget_title

    @app.callback(
        [Output("deprivation-bar-chart", "figure"), Output("deprivation-widget-title", "children")],
        [Input("selected-neighbourhood-store", "data"), Input("apply-filters-btn", "n_clicks")],
        [State("deprivation-category-dropdown", "value")]
    )
    def update_deprivation_widget(selected_neighbourhood, n_clicks, deprivation_category):
        widget_title = "#### Deprivation for Cardiff"
        chart_title = "Households by Deprivation Percentile"
        filtered_df = deprivation_df.copy()

        if selected_neighbourhood:
            name = selected_neighbourhood.get('NAME')
            if name:
                widget_title = f"#### Deprivation for {name}"
                poly_row = neighbourhoods_df[neighbourhoods_df['NAME'] == name]
                if not poly_row.empty:
                    neighbourhood_polygon = Polygon(poly_row.iloc[0]['contour'])

                    def is_in_neighbourhood(row):
                        dep_poly = Polygon(row['contour'])
                        return neighbourhood_polygon.contains(dep_poly.representative_point())

                    mask = filtered_df.apply(is_in_neighbourhood, axis=1)
                    filtered_df = filtered_df[mask]

        category_col = "Household deprivation (6 categories)"
        if deprivation_category:
            if deprivation_category == '4+':
                keywords = ['four', 'five', 'six']
                mask = filtered_df[category_col].str.contains('|'.join(keywords), na=False, case=False)
                filtered_df = filtered_df[mask]
            else:
                filtered_df = filtered_df[filtered_df[category_col] == deprivation_category]

        fig = create_deprivation_bar_chart(filtered_df, title=chart_title)
        return fig, widget_title

