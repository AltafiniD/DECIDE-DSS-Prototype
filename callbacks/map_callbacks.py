# callbacks/map_callbacks.py

from dash.dependencies import Input, Output, State
from dash import ctx
import pydeck as pdk
import pandas as pd
import numpy as np
import json

from config import INITIAL_VIEW_STATE_CONFIG, LAYER_CONFIG, MAP_STYLES
from utils.cache import get_dataframe

def register_callbacks(app, all_layers_config):
    """
    Registers all map-related callbacks to the Dash app.
    Receives layer configurations to dynamically build layers.
    """
    other_layer_ids = [k for k in LAYER_CONFIG.keys() if not k.startswith('crime_')]
    layer_toggle_inputs = [Input(f"{layer_id}-toggle", "value") for layer_id in other_layer_ids]
    
    style_btn_inputs = [Input(f"style-btn-{label.lower()}", "n_clicks") for label in MAP_STYLES.keys()]

    @app.callback(
        [Output("deck-gl", "data"), Output("layers-loading-output", "children")],
        [
            Input("apply-filters-btn", "n_clicks"),
            Input("crimes-master-toggle", "value"),
            Input("crime-viz-radio", "value"),
            *layer_toggle_inputs,
            *style_btn_inputs
        ],
        [
            State("time-filter-slider", "value"),
            State("crime-type-filter-dropdown", "value"),
            State("month-map-store", "data"),
            State("network-metric-dropdown", "value"),
            State("network-range-slider", "value"),
            State("deck-gl", "data")
        ]
    )
    def update_map_view(n_clicks, crime_master_toggle, crime_viz_selection, *args):
        num_other_layers = len(other_layer_ids)
        num_style_btns = len(MAP_STYLES)
        
        layer_toggles = args[:num_other_layers]
        style_btn_clicks = args[num_other_layers : num_other_layers + num_style_btns]
        time_range, selected_crime_types, month_map, network_metric, network_range, current_deck_json = args[num_other_layers + num_style_btns:]

        current_deck_dict = json.loads(current_deck_json) if isinstance(current_deck_json, str) else current_deck_json or {}

        trigger = ctx.triggered_id
        map_style = current_deck_dict.get('mapStyle', MAP_STYLES['Light'])
        if trigger and 'style-btn' in trigger:
            style_label = trigger.replace('style-btn-', '').capitalize()
            map_style = MAP_STYLES.get(style_label, map_style)

        visible_layers = []
        render_message = None

        # --- Crime Layer Filtering ---
        if crime_master_toggle and 'crimes' in crime_master_toggle:
            active_crime_layer_config = all_layers_config.get(crime_viz_selection)
            if active_crime_layer_config:
                crime_df_id = 'crime_points' if 'points' in crime_viz_selection else 'crime_heatmap'
                crime_df = get_dataframe(crime_df_id)
                
                masks = []
                if time_range and month_map:
                    start_month_str, end_month_str = month_map.get(str(time_range[0])), month_map.get(str(time_range[1]))
                    if start_month_str and end_month_str:
                        if 'Month_dt' not in crime_df.columns or crime_df['Month_dt'].dtype != 'datetime64[ns]':
                             crime_df['Month_dt'] = pd.to_datetime(crime_df['Month'], errors='coerce')
                        start_date, end_date = pd.to_datetime(start_month_str), pd.to_datetime(end_month_str)
                        masks.append(crime_df['Month_dt'].between(start_date, end_date))
                
                if selected_crime_types:
                    masks.append(crime_df['Crime type'].isin(selected_crime_types))
                
                filtered_crime_df = crime_df[np.all(masks, axis=0)] if masks else crime_df
                
                layer_args = active_crime_layer_config['args'].copy()
                layer_args['data'] = filtered_crime_df
                new_crime_layer = pdk.Layer(active_crime_layer_config['type'], **layer_args)
                visible_layers.append(new_crime_layer)

        # --- Dynamic Network Layer Filtering ---
        network_layer_config = all_layers_config.get('network')
        is_network_visible = any('network' in toggle for toggle in layer_toggles if toggle)
        if network_layer_config and is_network_visible and network_metric and network_range:
            network_df = get_dataframe('network')
            network_df[network_metric] = pd.to_numeric(network_df[network_metric], errors='coerce')
            
            mask = network_df[network_metric].between(network_range[0], network_range[1], inclusive='both')
            filtered_network_df = network_df[mask].copy()
            
            metric_series = filtered_network_df[network_metric].dropna()
            if not metric_series.empty:
                min_val, max_val = metric_series.min(), metric_series.max()
                
                if max_val == min_val:
                    norm_values = np.full(len(metric_series), 0.5)
                else:
                    norm_values = (metric_series - min_val) / (max_val - min_val)
                
                # THE FIX: Convert the numpy arrays to a list of lists of standard Python integers.
                # This is guaranteed to be JSON serializable and will fix the TypeError.
                red_channel = (255 * norm_values)
                green_channel = (255 * (1 - norm_values))
                blue_channel = np.zeros(len(metric_series))
                
                colours = np.stack([red_channel, green_channel, blue_channel], axis=1).astype(int).tolist()
                
                filtered_network_df['colour'] = colours
                filtered_network_df['value'] = metric_series
                filtered_network_df['metric'] = network_metric
            
            layer_args = network_layer_config['args'].copy()
            layer_args['data'] = filtered_network_df
            # Ensure the layer uses the new 'colour' column
            layer_args['get_color'] = 'colour'
            new_network_layer = pdk.Layer(network_layer_config['type'], **layer_args)
            visible_layers.append(new_network_layer)
        
        # --- Other Static Layers ---
        for i, layer_id in enumerate(other_layer_ids):
            is_toggled_on = i < len(layer_toggles) and layer_toggles[i]
            if is_toggled_on and layer_id in all_layers_config and layer_id != 'network':
                layer_config = all_layers_config[layer_id]
                visible_layers.append(pdk.Layer(layer_config['type'], **layer_config['args']))

        # --- Final Deck Assembly ---
        updated_view_state = pdk.ViewState(**INITIAL_VIEW_STATE_CONFIG)
        active_tooltip = True
        for layer in reversed(visible_layers):
            layer_config = LAYER_CONFIG.get(layer.id, {})
            if layer_config.get("tooltip"):
                active_tooltip = layer_config["tooltip"]; break

        deck = pdk.Deck(layers=visible_layers, initial_view_state=updated_view_state, map_style=map_style, tooltip=active_tooltip)
        
        return deck.to_json(), render_message
