# callbacks/map_callbacks.py

from dash.dependencies import Input, Output, State
from dash import no_update
import pydeck as pdk
import pandas as pd
import numpy as np
import jenkspy

from config import INITIAL_VIEW_STATE_CONFIG, LAYER_CONFIG, FLOOD_LAYER_CONFIG, BUILDING_COLOR_CONFIG

def register_callbacks(app, all_layers, dataframes):
    """
    Registers all map-related callbacks to the Dash app.
    """
    @app.callback(
        [Output("deck-gl", "data"), Output("layers-loading-output", "children")],
        [Input("map-update-trigger-store", "data")],
        [State("month-map-store", "data"), State("sas-month-map-store", "data")],
        prevent_initial_call=True
    )
    def update_map_view(trigger_data, crime_month_map, sas_month_map):
        if not trigger_data:
            return no_update, no_update

        def sanitize_data_for_json(df):
            df_copy = df.copy()
            df_copy.replace({pd.NA: None, np.nan: None, pd.NaT: None}, inplace=True)
            return df_copy.to_dict('records')

        map_style = trigger_data["map_style"]
        crime_viz_selection = trigger_data["crime_viz"]
        
        all_toggle_ids = [k for k, v in LAYER_CONFIG.items() if not k.startswith('crime_')]
        toggles_dict = dict(zip(all_toggle_ids, trigger_data["toggles"]))
        
        flooding_toggle = toggles_dict.get('flooding_toggle', False)
        
        time_range, selected_crime_types, network_metric, network_range, \
        deprivation_category, selected_land_use, flood_selection, \
        building_color_metric, selected_neighbourhoods, sas_object_search, sas_time_range = trigger_data["states"]

        visible_layers = []
        
        master_layer_order = list(LAYER_CONFIG.keys()) + list(FLOOD_LAYER_CONFIG.keys())

        for layer_id in master_layer_order:
            if layer_id not in all_layers:
                continue

            layer_type, original_args = all_layers[layer_id]
            new_layer_args = original_args.copy()
            df_to_process = dataframes[layer_id].copy()
            
            should_render = False

            if layer_id.startswith('crime_'):
                if crime_viz_selection == layer_id:
                    should_render = True
                    if time_range and isinstance(time_range, list) and len(time_range) == 2 and crime_month_map:
                        start_month_str, end_month_str = crime_month_map.get(str(time_range[0])), crime_month_map.get(str(time_range[1]))
                        if start_month_str and end_month_str:
                            df_to_process['Month_dt'] = pd.to_datetime(df_to_process['Month'], errors='coerce')
                            start_date, end_date = pd.to_datetime(start_month_str), pd.to_datetime(end_month_str)
                            df_to_process = df_to_process[(df_to_process['Month_dt'] >= start_date) & (df_to_process['Month_dt'] <= end_date)]
                    if selected_crime_types:
                        df_to_process = df_to_process[df_to_process['Crime type'].isin(selected_crime_types)]
            
            elif layer_id in FLOOD_LAYER_CONFIG:
                layer_config_id = FLOOD_LAYER_CONFIG[layer_id].get('id')
                if flooding_toggle and flood_selection and layer_config_id in flood_selection:
                    should_render = True
            
            elif layer_id in LAYER_CONFIG:
                if toggles_dict.get(layer_id):
                    should_render = True
                    
                    # FIXED: Added population layer coloring with 10 Jenks breaks
                    if layer_id == 'population':
                        if 'density' in df_to_process.columns:
                            density_series = pd.to_numeric(df_to_process['density'], errors='coerce').dropna()
                            if not density_series.empty and len(density_series.unique()) >= 2:
                                try:
                                    # Calculate 10 Jenks breaks
                                    breaks = jenkspy.jenks_breaks(density_series, n_classes=10)
                                    unique_breaks = sorted(list(set(breaks)))
                                    
                                    # Assign each area to a break class (0-9)
                                    df_to_process['jenks_class'] = pd.cut(
                                        df_to_process['density'], 
                                        bins=unique_breaks, 
                                        labels=False, 
                                        include_lowest=True
                                    )
                                    
                                    # 10-color gradient matching the widget
                                    color_palette = [
                                        [13, 34, 88],     # Darkest (Dark Blue/Purple)
                                        [14, 107, 140],
                                        [33, 151, 176],
                                        [64, 190, 175],
                                        [101, 212, 150],
                                        [139, 230, 125],
                                        [174, 242, 88],
                                        [203, 247, 56],
                                        [225, 247, 37],
                                        [240, 249, 33]    # Lightest (Yellow)
                                    ]
                                    
                                    # Map class to color with alpha
                                    df_to_process['color'] = df_to_process['jenks_class'].apply(
                                        lambda c: color_palette[int(c)] + [180] if pd.notna(c) else [200, 200, 200, 100]
                                    )
                                    new_layer_args['get_fill_color'] = 'color'
                                except Exception as e:
                                    print(f"Error calculating Jenks breaks for population: {e}")
                                    # Fallback to default coloring
                                    pass
                    
                    elif layer_id == 'buildings':
                        metric_config = BUILDING_COLOR_CONFIG.get(building_color_metric)
                        if metric_config and building_color_metric != 'none':
                            column_name = metric_config['column']
                            colors = metric_config['colors']
                            white_color = [255, 255, 255, 255]
                            def get_building_color(risk_level):
                                risk_level_str = str(risk_level).lower()
                                return colors.get(risk_level_str, white_color)
                            if column_name in df_to_process.columns:
                                df_to_process['color'] = df_to_process[column_name].apply(get_building_color)
                                new_layer_args['get_fill_color'] = 'color'
                        else:
                            new_layer_args['get_fill_color'] = BUILDING_COLOR_CONFIG['none']['color']

                    elif layer_id == 'stop_and_search':
                        if sas_time_range and isinstance(sas_time_range, list) and len(sas_time_range) == 2 and sas_month_map:
                            start_month_str, end_month_str = sas_month_map.get(str(sas_time_range[0])), sas_month_map.get(str(sas_time_range[1]))
                            if start_month_str and end_month_str:
                                df_to_process['Month_dt'] = pd.to_datetime(df_to_process['Date'], errors='coerce').dt.tz_localize(None)
                                start_date, end_date = pd.to_datetime(start_month_str), pd.to_datetime(end_month_str)
                                df_to_process = df_to_process[(df_to_process['Month_dt'] >= start_date) & (df_to_process['Month_dt'] <= end_date)]
                        if sas_object_search:
                            df_to_process = df_to_process[df_to_process['Object of search'].isin(sas_object_search)]
                    
                    elif layer_id == 'network' and network_metric and network_range:
                        if network_metric in df_to_process.columns:
                            df_to_process[network_metric] = pd.to_numeric(df_to_process[network_metric], errors='coerce')
                            mask = (df_to_process[network_metric] >= network_range[0]) & (df_to_process[network_metric] <= network_range[1])
                            df_to_process = df_to_process[mask]
                            metric_series = df_to_process[network_metric].dropna()
                            if not metric_series.empty:
                                try:
                                    decile_labels = pd.qcut(metric_series, 10, labels=False, duplicates='drop')
                                    df_to_process['decile'] = decile_labels
                                    if 'risk' in network_metric.lower():
                                        blue_hex = ['#eff3ff', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b', '#08306b', '#08306b']
                                        decile_colors = [list(tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))) + [220] for h in blue_hex]
                                        df_to_process['color'] = df_to_process['decile'].apply(lambda d: decile_colors[int(d)] if pd.notna(d) else [128, 128, 128, 150])
                                    else:
                                        df_to_process['color'] = df_to_process['decile'].apply(lambda d: [int(255 * (d/9.0 * 2)) if d/9.0 > 0.5 else 0, int(255 * (1 - abs(d/9.0 - 0.5) * 2)), int(255 * (1 - d/9.0 * 2)) if d/9.0 < 0.5 else 0, 150] if pd.notna(d) else [128, 128, 128, 150])
                                    df_to_process['value'] = metric_series; df_to_process['metric'] = network_metric
                                except (ValueError, IndexError):
                                    df_to_process['color'] = [[128, 128, 128, 150]] * len(df_to_process)

                    elif layer_id == 'deprivation' and deprivation_category:
                        category_col = "Household deprivation (6 categories)"
                        if deprivation_category == '4+':
                            keywords = ['four', 'five', 'six']
                            mask = df_to_process[category_col].str.contains('|'.join(keywords), na=False, case=False)
                            df_to_process = df_to_process[mask]
                        else:
                            df_to_process = df_to_process[df_to_process[category_col] == deprivation_category]

                    elif layer_id == 'land_use' and selected_land_use:
                        df_to_process = df_to_process[df_to_process['landuse_text'].isin(selected_land_use)]
                    
                    elif layer_id == 'neighbourhoods' and selected_neighbourhoods:
                        df_to_process = df_to_process[df_to_process['NAME'].isin(selected_neighbourhoods)]

            if should_render:
                new_layer_args['data'] = sanitize_data_for_json(df_to_process)
                visible_layers.append(pdk.Layer(layer_type, **new_layer_args))

        view_config = INITIAL_VIEW_STATE_CONFIG.copy()
        updated_view_state = pdk.ViewState(**view_config, transition_duration=250)
        
        active_tooltip = None
        for layer in reversed(visible_layers):
            if hasattr(layer, 'id'):
                layer_id = layer.id
                layer_key = next((k for k, v in {**LAYER_CONFIG, **FLOOD_LAYER_CONFIG}.items() if v.get('id') == layer_id), None)
                if layer_key:
                    config = {**LAYER_CONFIG, **FLOOD_LAYER_CONFIG}[layer_key]
                    tooltip_config = config.get("tooltip")
                    if tooltip_config:
                        active_tooltip = tooltip_config
                        break
        
        deck = pdk.Deck(layers=visible_layers, initial_view_state=updated_view_state, map_style=map_style, tooltip=active_tooltip if active_tooltip else True)
        
        return deck.to_json(), None

