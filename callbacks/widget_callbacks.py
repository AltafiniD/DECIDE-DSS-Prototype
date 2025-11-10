# callbacks/widget_callbacks.py

import dash
from dash.dependencies import Input, Output, State
from dash import no_update, ctx, html, dcc
import pandas as pd
import json

from config import LAYER_CONFIG
from utils.geometry import is_point_in_polygon
from utils.colours import get_crime_colour_map
from components.crime_widget import create_crime_histogram_figure
from components.network_widget import create_network_histogram_figure
from components.flood_risk_widget import create_flood_risk_chart
from components.land_use_widget import create_land_use_chart, create_high_level_land_use_chart
from components.jenks_histogram_widget import create_jenks_histogram_figure
from components.buildings_at_risk_widget import create_buildings_at_risk_widget
from components.deprivation_widget import create_deprivation_bar_chart
from components.population_widget import create_combined_population_widget
from components.stop_and_search_widget import create_stop_and_search_histogram_figure
from components.sas_gender_widget import create_sas_gender_pie_chart
from shapely.geometry import Point, Polygon

def register_callbacks(app, crime_df, neighbourhoods_df, network_df, buildings_df, land_use_df, deprivation_df, population_df, stop_and_search_df):
    """
    Registers all widget-related callbacks.
    """
    plotly_colour_map, _ = get_crime_colour_map()

    # Helper: map toggles from LAYER_CONFIG order (non-crime layers) to incoming toggles list
    def map_toggles(trigger):
        keys = [k for k in LAYER_CONFIG.keys() if not k.startswith('crime_')]
        toggles = trigger.get("toggles", []) if trigger else []
        return {k: (toggles[i] if i < len(toggles) else False) for i, k in enumerate(keys)}

    # Helper: safe check for chart click containing customdata
    def click_has_customdata(click):
        return bool(click and click.get('points') and click['points'][0].get('customdata'))

    @app.callback(
        Output("widget-grid-container", "children"),
        Input("map-update-trigger-store", "data"),
        State("sas-month-map-store", "data"),
        prevent_initial_call=True
    )
    def update_widget_panel(trigger_data, sas_month_map):
        if not trigger_data:
            return no_update

        crime_viz_selection = trigger_data.get("crime_viz")
        toggles_dict = map_toggles(trigger_data)
        
        states = trigger_data.get("states", [])
        selected_sas_objects = states[9] if len(states) > 9 else []
        sas_time_range = states[10] if len(states) > 10 else []

        all_widgets = []
        
        # --- Stop & Search Widgets ---
        if toggles_dict.get('stop_and_search'):
            
            filtered_sas_df = stop_and_search_df.copy()
            
            if sas_time_range and sas_month_map:
                start_month_str, end_month_str = sas_month_map.get(str(sas_time_range[0])), sas_month_map.get(str(sas_time_range[1]))
                if start_month_str and end_month_str:
                    filtered_sas_df['Month_dt'] = pd.to_datetime(filtered_sas_df['Date'], errors='coerce').dt.to_period('M').dt.to_timestamp()
                    start_date, end_date = pd.to_datetime(start_month_str), pd.to_datetime(end_month_str)
                    filtered_sas_df = filtered_sas_df[(filtered_sas_df['Month_dt'] >= start_date) & (filtered_sas_df['Month_dt'] <= end_date)]

            if selected_sas_objects:
                filtered_sas_df = filtered_sas_df[filtered_sas_df['Object of search'].isin(selected_sas_objects)]

            sas_fig = create_stop_and_search_histogram_figure(filtered_sas_df)
            sas_gender_fig = create_sas_gender_pie_chart(filtered_sas_df)
            
            # MODIFIED: Create histogram widget to take full width
            sas_histogram = html.Div(className="widget", children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
                    dcc.Markdown("#### Stop & Search Events"),
                    html.Button("Clear Filter", id="clear-sas-filter-btn", n_clicks=0, style={'fontSize': '12px'})
                ]),
                dcc.Graph(id="stop-and-search-chart", figure=sas_fig, style={'height': '500px'})
            ])
            
            # The container (html.Div) is now 50% wide, and the chart fills it
            sas_pie = html.Div(
                className="widget",
                    style={'width': '49%', 'display': 'inline-block', 'margin': '0.5%'}, # Set container width
                    children=[
                    dcc.Markdown("#### S&S Gender Distribution"),
                    dcc.Graph(id="sas-gender-pie-chart", figure=sas_gender_fig, style={'height': '250px'})
            ])

            #--------------- MODIFIED: Stack histogram and pie chart vertically instead of side by side---------------
            # 2. Define a second half-width widget (a placeholder)
            #other_widget_half = html.Div(className="widget", style={'width': '50%'}, children=[
            #dcc.Markdown("#### Another Widget"),
            # ... content for the other widget ...

            # 3. Create a flex container to hold them horizontally
            #horizontal_container = html.Div(
            #style={'display': 'flex', 'gap': '10px'},
            #children=[sas_pie_half, other_widget_half]
            #--------------- MODIFIED: Stack histogram and pie chart vertically instead of side by side---------------
            
            # MODIFIED: Stack them vertically instead of horizontally
            all_widgets.append(sas_histogram)
            all_widgets.append(sas_pie)

        # --- Crime Widget ---
        if crime_viz_selection:
            initial_crime_fig = create_crime_histogram_figure(crime_df) 
            all_widgets.append(html.Div(className="widget", children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
                    dcc.Markdown(id="crime-widget-title", children="#### Crime Statistics"),
                    html.Button("Clear Selection", id="clear-crime-filter-btn", n_clicks=0, style={'fontSize': '12px'})]),
                dcc.Graph(id="crime-bar-chart", figure=initial_crime_fig, style={'height': '500px'})
            ]))

        # --- Network Widgets ---
        if toggles_dict.get('network'):
            initial_metric = 'NACH_rivers_risk' if 'NACH_rivers_risk' in network_df.columns else ('NAIN' if 'NAIN' in network_df.columns else None)
            series = network_df[initial_metric] if initial_metric and not network_df.empty else pd.Series()
            initial_network_fig = create_network_histogram_figure(series, initial_metric)
            initial_jenks_fig = create_jenks_histogram_figure(series, initial_metric)
            
            network_hist = html.Div(className="widget", children=[dcc.Markdown("#### Network Metric (Deciles)"), dcc.Graph(id="network-histogram-chart", figure=initial_network_fig, style={'height': '220px'})])
            jenks_hist = html.Div(className="widget", children=[dcc.Markdown("#### Network Metric (Jenks)"), dcc.Graph(id="jenks-histogram-chart", figure=initial_jenks_fig, style={'height': '220px'})])
            
            # MODIFIED: Append histograms as separate widgets to stack them vertically
            all_widgets.append(network_hist)
            all_widgets.append(jenks_hist)
        
        # --- Buildings Widget ---
        if toggles_dict.get('flooding_toggle'):
            all_widgets.append(html.Div(className="widget", children=[
                dcc.Markdown("#### Buildings"),
                html.Div("Total Buildings: 150.504", id="total-buildings-placeholder", style={'padding': '6px', 'fontWeight': '600'})
            ]))

        # --- Flooding Widgets ---            
            buildings_at_risk_cards = create_buildings_at_risk_widget(buildings_df)
            all_widgets.append(html.Div(className="widget", children=[
                dcc.Markdown("#### Buildings at Hazard Summary (Recurrence Interval)"),
                buildings_at_risk_cards
            ]))
            
            initial_flood_fig = create_flood_risk_chart(buildings_df, ['river_hazard'], title="")
            all_widgets.append(html.Div(className="widget widget-full-width", children=[ # Added widget-full-width here
                dcc.Markdown("#### Building Flood Hazard (Recurrence Interval)"),
                dcc.Checklist(
                    id='flood-risk-type-selector',
                    options=[
                        {'label': 'Rivers', 'value': 'river_hazard'},
                        {'label': 'Surface Water', 'value': 'surface_hazard'},
                        {'label': 'Sea', 'value': 'sea_hazard'},
                    ],
                    value=['river_hazard'],
                    labelStyle={'display': 'inline-block', 'margin-right': '10px'}
                ),
                dcc.Graph(id="flood-risk-chart", figure=initial_flood_fig)
            ]))

        # --- Land Use Widget ---
        if toggles_dict.get('land_use'):
            initial_land_use_fig = create_land_use_chart(land_use_df, title="Cardiff Land Use")
            initial_high_level_fig = create_high_level_land_use_chart(land_use_df, title="High-Level Land Use")
            
            detailed_widget = html.Div(className="widget", children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
                    dcc.Markdown(id="land-use-widget-title", children="#### Land Use (Detailed)"), 
                    html.Button("Clear Filter", id="clear-land-use-filter-btn", n_clicks=0, style={'fontSize': '12px'})
                ]), 
                dcc.Graph(id="land-use-chart", figure=initial_land_use_fig, config={'displayModeBar': False})
            ])
            
            high_level_widget = html.Div(className="widget", children=[
                dcc.Markdown(id="high-level-land-use-widget-title", children="#### Land Use (High-Level)"), 
                dcc.Graph(id="high-level-land-use-chart", figure=initial_high_level_fig, config={'displayModeBar': False})
            ])
            
            all_widgets.append(html.Div([detailed_widget, high_level_widget], style={'display': 'flex', 'gap': '10px', 'flexDirection': 'column'}))

        # --- Deprivation Widget ---
        if toggles_dict.get('deprivation'):
            initial_deprivation_fig = create_deprivation_bar_chart(deprivation_df)
            all_widgets.append(html.Div(className="widget", children=[
                dcc.Markdown(id="deprivation-widget-title", children="#### Household Deprivation"), 
                dcc.Graph(id="deprivation-bar-chart", figure=initial_deprivation_fig, style={'height': '220px'})
            ]))

        # --- Population Widgets ---
        if toggles_dict.get('population'):
            # MODIFIED: Use the combined population widget
            population_widget_combined = create_combined_population_widget(population_df)
            all_widgets.append(population_widget_combined)

        return all_widgets if all_widgets else []

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
        if not click_has_customdata(chart_click):
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
        Output('sas-object-filter-dropdown', 'value'),
        Output('apply-filters-btn', 'n_clicks', allow_duplicate=True),
        Input('stop-and-search-chart', 'clickData'),
        State('apply-filters-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_sas_filter_from_graph_click(chart_click, n_clicks):
        if not click_has_customdata(chart_click):
            return no_update, no_update
        
        object_of_search = chart_click['points'][0]['customdata'][0]
        return [object_of_search], (n_clicks or 0) + 1

    @app.callback(
        Output('sas-object-filter-dropdown', 'value', allow_duplicate=True),
        Output('apply-filters-btn', 'n_clicks', allow_duplicate=True),
        Input('clear-sas-filter-btn', 'n_clicks'),
        State('apply-filters-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_sas_graph_filter(clear_clicks, n_clicks):
        if not clear_clicks or clear_clicks == 0:
            return no_update, no_update
        return [], (n_clicks or 0) + 1

    @app.callback(
        [Output("crime-bar-chart", "figure"), Output("crime-widget-title", "children")],
        [Input("selected-neighbourhood-store", "data"), Input("apply-filters-btn", "n_clicks")],
        [State("time-filter-slider", "value"), State("crime-type-filter-dropdown", "value"), State("month-map-store", "data")]
    )
    def update_crime_widget(selected_neighbourhood, n_clicks, time_range, selected_crime_types, month_map):
        widget_title = "#### Crime Statistics"
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

        fig = create_crime_histogram_figure(df_to_filter, title=chart_title) 
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
        Output("flood-risk-chart", "figure"),
        Input("flood-risk-type-selector", "value")
    )
    def update_flood_risk_widget(risk_type):
        if not risk_type:
            return no_update

        selected = risk_type if isinstance(risk_type, (list, tuple)) else [risk_type]
        fig = create_flood_risk_chart(buildings_df, selected, title="")
        return fig

    @app.callback(
        Output('land-use-type-dropdown', 'value'),
        Output('apply-filters-btn', 'n_clicks', allow_duplicate=True),
        Input('land-use-chart', 'clickData'),
        State('apply-filters-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_filter_from_land_use_click(chart_click, n_clicks):
        if not click_has_customdata(chart_click):
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
        [
            Output("land-use-chart", "figure"), 
            Output("land-use-widget-title", "children"),
            Output("high-level-land-use-chart", "figure"),
            Output("high-level-land-use-widget-title", "children")
        ],
        [Input("selected-neighbourhood-store", "data"), Input("apply-filters-btn", "n_clicks")],
        [State("land-use-type-dropdown", "value")]
    )
    def update_land_use_widget(selected_neighbourhood, n_clicks, selected_land_use):
        widget_title = "#### Land Use (Detailed)"
        high_level_title = "#### Land Use (High-Level)"
        chart_title = "Land Use Distribution"

        df_to_filter = land_use_df.copy()

        if selected_neighbourhood:
            name = selected_neighbourhood.get('NAME')
            if name:
                widget_title = f"#### Land Use (Detailed) for {name}"
                high_level_title = f"#### Land Use (High-Level) for {name}"
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

        detailed_fig = create_land_use_chart(df_to_filter, title=chart_title)
        high_level_fig = create_high_level_land_use_chart(df_to_filter, title=chart_title)
        
        return detailed_fig, widget_title, high_level_fig, high_level_title

    @app.callback(
        [Output("deprivation-bar-chart", "figure"), Output("deprivation-widget-title", "children")],
        [Input("selected-neighbourhood-store", "data"), Input("apply-filters-btn", "n_clicks")],
        [State("deprivation-category-dropdown", "value")]
    )
    def update_deprivation_widget(selected_neighbourhood, n_clicks, deprivation_category):
        widget_title = "#### Households Deprivation"
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
