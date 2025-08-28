# callbacks/map_callbacks.py

from dash.dependencies import Input, Output, State
from dash import no_update
import pydeck as pdk
import copy
import pandas as pd
import numpy as np

from config import INITIAL_VIEW_STATE_CONFIG, LAYER_CONFIG, FLOOD_LAYER_CONFIG, BUILDING_COLOR_CONFIG

def register_callbacks(app, all_layers, dataframes):
    """
    Registers all map-related callbacks to the Dash app.
    """
    @app.callback(
        [Output("deck-gl", "data"), Output("layers-loading-output", "children")],
        Input("map-update-trigger-store", "data"),
        State("month-map-store", "data"),
        prevent_initial_call=True
    )
    def update_map_view(trigger_data, month_map):
        """
        This callback reconstructs the map and controls the loading spinner.
        It's triggered only when the aggregated input data changes in the store.
        """
        if not trigger_data:
            return no_update, no_update

        # Unpack all the values from the trigger_data dictionary
        map_style = trigger_data["map_style"]
        crime_viz_selection = trigger_data["crime_viz"]
        
        flooding_toggle, *other_toggles = trigger_data["toggles"]
        
        time_range, selected_crime_types, network_metric, network_range, \
        deprivation_category, flood_selection, building_color_metric = trigger_data["states"]

        visible_layers = []
        other_layer_ids = [k for k, v in LAYER_CONFIG.items() if not k.startswith('crime_') and v.get('type') != 'toggle_only']

        if crime_viz_selection and crime_viz_selection in all_layers:
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

        if flooding_toggle and flood_selection:
            for layer_id in flood_selection:
                if layer_id in all_layers:
                    visible_layers.append(all_layers[layer_id])

        for i, layer_id in enumerate(other_layer_ids):
            if i < len(other_toggles) and other_toggles[i]:
                if layer_id == 'buildings':
                    metric_config = BUILDING_COLOR_CONFIG.get(building_color_metric)
                    buildings_df = dataframes['buildings']
                    
                    building_layer_args = {
                        'id': 'buildings', 'data': buildings_df, 'pickable': True, 'extruded': True,
                        'wireframe': True, 'get_polygon': 'contour', 'get_elevation': 'height'
                    }

                    if metric_config and building_color_metric != 'none':
                        column_name = metric_config['column']
                        colors = metric_config['colors']
                        white_color = [255, 255, 255, 180]

                        def get_building_color(risk_level):
                            risk_level_str = str(risk_level).lower()
                            if risk_level_str == 'low': return colors.get('low', white_color)
                            if risk_level_str == 'medium': return colors.get('medium', white_color)
                            if risk_level_str == 'high': return colors.get('high', white_color)
                            return white_color

                        if column_name in buildings_df.columns:
                            buildings_df_copy = buildings_df.copy()
                            buildings_df_copy['color'] = buildings_df_copy[column_name].apply(get_building_color)
                            building_layer_args['data'] = buildings_df_copy
                            building_layer_args['get_fill_color'] = 'color'
                        else:
                            print(f"Warning: Column '{column_name}' not found for building coloring.")
                            building_layer_args['get_fill_color'] = BUILDING_COLOR_CONFIG['none']['color']
                    else:
                        building_layer_args['get_fill_color'] = BUILDING_COLOR_CONFIG['none']['color']
                    
                    new_building_layer = pdk.Layer("PolygonLayer", **building_layer_args)
                    visible_layers.append(new_building_layer)
                
                else:
                    layer_copy = copy.deepcopy(all_layers[layer_id])
                    if layer_id == 'network' and network_metric and network_range:
                        original_network_df = dataframes['network']
                        filtered_network_df = original_network_df.copy()
                        filtered_network_df[network_metric] = pd.to_numeric(filtered_network_df[network_metric], errors='coerce')
                        mask = (filtered_network_df[network_metric] >= network_range[0]) & (filtered_network_df[network_metric] <= network_range[1])
                        filtered_network_df = filtered_network_df[mask].copy()
                        metric_series = filtered_network_df[network_metric].dropna()
                        
                        if not metric_series.empty:
                            try:
                                decile_labels = pd.qcut(metric_series, 10, labels=False, duplicates='drop')
                                filtered_network_df['decile'] = decile_labels
                                
                                def get_rainbow_color(decile):
                                    if pd.isna(decile): return [128, 128, 128, 150]
                                    norm = decile / 9.0 
                                    r = int(255 * (norm * 2)) if norm > 0.5 else 0
                                    g = int(255 * (1 - abs(norm - 0.5) * 2))
                                    b = int(255 * (1 - norm * 2)) if norm < 0.5 else 0
                                    return [r, g, b, 150]

                                filtered_network_df['color'] = filtered_network_df['decile'].apply(get_rainbow_color)
                                filtered_network_df['value'] = metric_series
                                filtered_network_df['metric'] = network_metric
                            except ValueError:
                                filtered_network_df['color'] = [[128, 128, 128, 150]] * len(filtered_network_df)
                                print("Could not calculate deciles for network coloring.")

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
            if hasattr(layer, 'id') and (layer.id in LAYER_CONFIG or any(layer.id == f['id'] for f in FLOOD_LAYER_CONFIG.values())):
                layer_config = LAYER_CONFIG.get(layer.id)
                if not layer_config:
                    for f_id, f_config in FLOOD_LAYER_CONFIG.items():
                        if f_config['id'] == layer.id:
                            layer_config = f_config
                            break
                tooltip_config = layer_config.get("tooltip") if layer_config else None
                if tooltip_config:
                    active_tooltip = tooltip_config
                    break

        deck = pdk.Deck(layers=visible_layers, initial_view_state=updated_view_state, map_style=map_style, tooltip=active_tooltip if active_tooltip else True)
        
        return deck.to_json(), None
