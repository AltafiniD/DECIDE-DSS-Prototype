# callbacks/map_callbacks.py

from dash.dependencies import Input, Output, State
import pydeck as pdk
import copy
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
            # Input("perspective-slider", "value"), # --- REMOVED ---
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
        ]
    )
    def update_map_view(n_clicks, map_style, crime_viz_selection, *args):
        """
        This callback reconstructs the map with the correct layers, view, and style.
        """
        num_toggles = len(other_layer_ids)
        layer_toggles = args[:num_toggles]
        time_range, selected_crime_types, month_map, network_metric, network_range = args[num_toggles:]

        visible_layers = []
        layers_to_render = copy.deepcopy(all_layers)

        # --- Crime Layer Filtering ---
        active_crime_layer = layers_to_render.get(crime_viz_selection)
        if active_crime_layer:
            crime_df_id = 'crime_points' if 'points' in crime_viz_selection else 'crime_heatmap'
            filtered_crime_df = dataframes[crime_df_id].copy()
            if time_range and month_map:
                start_month_str, end_month_str = month_map.get(str(time_range[0])), month_map.get(str(time_range[1]))
                if start_month_str and end_month_str:
                    filtered_crime_df['Month_dt'] = pd.to_datetime(filtered_crime_df['Month'], errors='coerce')
                    start_date, end_date = pd.to_datetime(start_month_str), pd.to_datetime(end_month_str)
                    filtered_crime_df = filtered_crime_df[(filtered_crime_df['Month_dt'] >= start_date) & (filtered_crime_df['Month_dt'] <= end_date)]
            if selected_crime_types:
                filtered_crime_df = filtered_crime_df[filtered_crime_df['Crime type'].isin(selected_crime_types)]
            active_crime_layer.data = filtered_crime_df
            visible_layers.append(active_crime_layer)

        # --- Dynamic Network Layer Filtering and Coloring ---
        network_layer = layers_to_render.get('network')
        is_network_visible = any('network' in toggle for toggle in layer_toggles if toggle)
        if network_layer and is_network_visible and network_metric and network_range:
            network_df = dataframes['network'].copy()
            network_df[network_metric] = pd.to_numeric(network_df[network_metric], errors='coerce')
            
            mask = (network_df[network_metric] >= network_range[0]) & (network_df[network_metric] <= network_range[1])
            filtered_network_df = network_df[mask].copy()

            metric_series = filtered_network_df[network_metric].dropna()
            if not metric_series.empty:
                min_val, max_val = metric_series.min(), metric_series.max()
                if max_val == min_val:
                    norm_series = pd.Series(0.5, index=metric_series.index)
                else:
                    norm_series = (metric_series - min_val) / (max_val - min_val)
                
                def get_rainbow_color(norm):
                    if pd.isna(norm): return [128, 128, 128, 100]
                    r = int(255 * (norm * 2)) if norm > 0.5 else 0
                    g = int(255 * (1 - abs(norm - 0.5) * 2))
                    b = int(255 * (1 - norm * 2)) if norm < 0.5 else 0
                    return [r, g, b, 150]

                filtered_network_df['color'] = norm_series.apply(get_rainbow_color)
                filtered_network_df['value'] = metric_series
                filtered_network_df['metric'] = network_metric
            
            network_layer.data = filtered_network_df
        
        for i, layer_id in enumerate(other_layer_ids):
            if i < len(layer_toggles) and layer_toggles[i] and layer_id in layers_to_render:
                visible_layers.append(layers_to_render[layer_id])

        # --- UPDATED: View state is no longer dynamic ---
        view_config = INITIAL_VIEW_STATE_CONFIG.copy()
        updated_view_state = pdk.ViewState(**view_config, transition_duration=250)
        
        active_tooltip = None
        for layer in reversed(visible_layers):
            layer_id = layer.id
            layer_config = LAYER_CONFIG.get(layer_id, {})
            tooltip_config = layer_config.get("tooltip")
            if tooltip_config:
                active_tooltip = tooltip_config
                break

        deck = pdk.Deck(layers=visible_layers, initial_view_state=updated_view_state, map_style=map_style, tooltip=active_tooltip if active_tooltip else True)
        
        return deck.to_json(), None