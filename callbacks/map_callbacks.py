# callbacks/map_callbacks.py

from dash.dependencies import Input, Output, State
import pydeck as pdk
import copy # --- IMPORT THE COPY MODULE ---
import pandas as pd
import numpy as np

from config import INITIAL_VIEW_STATE_CONFIG, LAYER_CONFIG

def register_callbacks(app, all_layers, dataframes):
    """
    Registers all map-related callbacks to the Dash app.
    """
    other_layer_ids = [k for k in LAYER_CONFIG.keys() if not k.startswith('crime_')]
    layer_toggle_inputs = [Input(f"{layer_id}-toggle", "value") for layer_id in other_layer_ids]

    @app.callback(
        [Output("deck-gl", "data"), Output("layers-loading-output", "children")],
        [
            Input("apply-filters-btn", "n_clicks"),
            Input("map-style-radio", "value"),
            Input("crime-viz-radio", "value"),
            *layer_toggle_inputs
        ],
        [
            State("time-filter-slider", "value"),
            State("crime-type-filter-dropdown", "value"),
            State("month-map-store", "data"),
            State("network-metric-dropdown", "value"),
            State("network-range-slider", "value"),
            State("deprivation-category-dropdown", "value")
        ]
    )
    def update_map_view(n_clicks, map_style, crime_viz_selection, *args):
        """
        This callback reconstructs the map with the correct layers, view, and style.
        """
        num_other_layers = len(other_layer_ids)
        layer_toggles = args[:num_other_layers]
        time_range, selected_crime_types, month_map, network_metric, network_range, deprivation_category = args[num_other_layers:]

        visible_layers = []

        # --- Crime Layer Filtering ---
        if crime_viz_selection and crime_viz_selection in all_layers:
            # --- CORRECTED: Use copy.deepcopy ---
            layer_copy = copy.deepcopy(all_layers[crime_viz_selection])
            
            crime_df_id = 'crime_points' if 'points' in crime_viz_selection else 'crime_heatmap'
            original_crime_df = dataframes[crime_df_id]
            filtered_crime_df = original_crime_df.copy()
            
            if time_range and month_map:
                start_month_str, end_month_str = month_map.get(str(time_range[0])), month_map.get(str(time_range[1]))
                if start_month_str and end_month_str:
                    filtered_crime_df['Month_dt'] = pd.to_datetime(filtered_crime_df['Month'], errors='coerce')
                    start_date, end_date = pd.to_datetime(start_month_str), pd.to_datetime(end_month_str)
                    filtered_crime_df = filtered_crime_df[(filtered_crime_df['Month_dt'] >= start_date) & (filtered_crime_df['Month_dt'] <= end_date)]
            if selected_crime_types:
                filtered_crime_df = filtered_crime_df[filtered_crime_df['Crime type'].isin(selected_crime_types)]
            
            layer_copy.data = filtered_crime_df
            visible_layers.append(layer_copy)

        # --- Handle visibility and filtering for other layers ---
        for i, layer_id in enumerate(other_layer_ids):
            if i < len(layer_toggles) and layer_toggles[i] and layer_id in all_layers:
                # --- CORRECTED: Use copy.deepcopy ---
                layer_copy = copy.deepcopy(all_layers[layer_id])
                
                if layer_id == 'network' and network_metric and network_range:
                    original_network_df = dataframes['network']
                    filtered_network_df = original_network_df.copy()
                    filtered_network_df[network_metric] = pd.to_numeric(filtered_network_df[network_metric], errors='coerce')
                    mask = (filtered_network_df[network_metric] >= network_range[0]) & (filtered_network_df[network_metric] <= network_range[1])
                    filtered_network_df = filtered_network_df[mask].copy()

                    metric_series = filtered_network_df[network_metric].dropna()
                    if not metric_series.empty:
                        min_val, max_val = metric_series.min(), metric_series.max()
                        norm_series = (metric_series - min_val) / (max_val - min_val) if max_val > min_val else 0.5
                        def get_rainbow_color(norm):
                            if pd.isna(norm): return [128, 128, 128, 100]
                            r = int(255 * (norm * 2)) if norm > 0.5 else 0
                            g = int(255 * (1 - abs(norm - 0.5) * 2))
                            b = int(255 * (1 - norm * 2)) if norm < 0.5 else 0
                            return [r, g, b, 150]
                        filtered_network_df['color'] = norm_series.apply(get_rainbow_color)
                        filtered_network_df['value'] = metric_series
                        filtered_network_df['metric'] = network_metric
                    layer_copy.data = filtered_network_df
                
                elif layer_id == 'deprivation' and deprivation_category and deprivation_category != 'all':
                    original_dep_df = dataframes['deprivation']
                    category_col = "Household deprivation (6 categories)"
                    filtered_dep_df = original_dep_df[original_dep_df[category_col] == deprivation_category].copy()
                    layer_copy.data = filtered_dep_df

                visible_layers.append(layer_copy)

        view_config = INITIAL_VIEW_STATE_CONFIG.copy()
        updated_view_state = pdk.ViewState(**view_config, transition_duration=250)
        
        active_tooltip = None
        for layer in reversed(visible_layers):
            # Ensure layer.id exists and is in LAYER_CONFIG
            if hasattr(layer, 'id') and layer.id in LAYER_CONFIG:
                layer_config = LAYER_CONFIG.get(layer.id, {})
                tooltip_config = layer_config.get("tooltip")
                if tooltip_config:
                    active_tooltip = tooltip_config
                    break

        deck = pdk.Deck(layers=visible_layers, initial_view_state=updated_view_state, map_style=map_style, tooltip=active_tooltip if active_tooltip else True)
        
        return deck.to_json(), None
