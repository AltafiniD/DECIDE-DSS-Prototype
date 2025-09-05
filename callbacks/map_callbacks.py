# callbacks/map_callbacks.py

from dash.dependencies import Input, Output, State
from dash import no_update
import pydeck as pdk
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
        if not trigger_data:
            return no_update, no_update

        # --- DEFINITIVE FIX: Robust Data Sanitization ---
        # This function converts a DataFrame into a format that is guaranteed to be
        # JSON-serializable by pydeck. It replaces all numpy/pandas nulls with
        # Python's None and then converts the DataFrame to a list of dictionaries,
        # which forces all special numeric types (e.g., int64) into standard Python types.
        def sanitize_data_for_json(df):
            df_copy = df.copy()
            # Replace all recognized null-like values with None
            df_copy.replace({pd.NA: None, np.nan: None, pd.NaT: None}, inplace=True)
            # Convert to a list of records to force all types to native Python
            return df_copy.to_dict('records')

        map_style = trigger_data["map_style"]
        crime_viz_selection = trigger_data["crime_viz"]
        
        all_toggle_ids = [k for k, v in LAYER_CONFIG.items() if not k.startswith('crime_')]
        toggles_dict = dict(zip(all_toggle_ids, trigger_data["toggles"]))
        
        flooding_toggle = toggles_dict.get('flooding_toggle', False)
        
        time_range, selected_crime_types, network_metric, network_range, \
        deprivation_category, selected_land_use, flood_selection, \
        building_color_metric, selected_neighbourhoods = trigger_data["states"]

        visible_layers = []
        
        # --- Handle Crime Layers ---
        if crime_viz_selection and crime_viz_selection in all_layers:
            layer_type, original_args = all_layers[crime_viz_selection]
            new_layer_args = original_args.copy()
            
            original_crime_df = dataframes[crime_viz_selection]
            filtered_crime_df = original_crime_df.copy()
            
            if time_range and month_map:
                start_month_str, end_month_str = month_map.get(str(time_range[0])), month_map.get(str(time_range[1]))
                if start_month_str and end_month_str:
                    filtered_crime_df['Month_dt'] = pd.to_datetime(filtered_crime_df['Month'], errors='coerce')
                    start_date, end_date = pd.to_datetime(start_month_str), pd.to_datetime(end_month_str)
                    filtered_crime_df = filtered_crime_df[(filtered_crime_df['Month_dt'] >= start_date) & (filtered_crime_df['Month_dt'] <= end_date)]
            
            if selected_crime_types:
                filtered_crime_df = filtered_crime_df[filtered_crime_df['Crime type'].isin(selected_crime_types)]
            
            new_layer_args['data'] = sanitize_data_for_json(filtered_crime_df)
            visible_layers.append(pdk.Layer(layer_type, **new_layer_args))

        # --- Handle Flood Layers ---
        if flooding_toggle and flood_selection:
            for layer_id in flood_selection:
                if layer_id in all_layers:
                    layer_type, layer_args = all_layers[layer_id]
                    new_args = layer_args.copy()
                    new_args['data'] = sanitize_data_for_json(layer_args['data'])
                    visible_layers.append(pdk.Layer(layer_type, **new_args))

        # --- Handle Other Toggleable Layers ---
        other_layer_ids = [k for k, v in LAYER_CONFIG.items() if not k.startswith('crime_') and v.get('type') != 'toggle_only']
        for layer_id in other_layer_ids:
            if toggles_dict.get(layer_id):
                layer_type, original_args = all_layers[layer_id]
                new_layer_args = original_args.copy()
                df_to_process = dataframes[layer_id].copy()

                if layer_id == 'buildings':
                    metric_config = BUILDING_COLOR_CONFIG.get(building_color_metric)
                    if metric_config and building_color_metric != 'none':
                        column_name = metric_config['column']
                        colors = metric_config['colors']
                        white_color = [255, 255, 255, 180]
                        def get_building_color(risk_level):
                            risk_level_str = str(risk_level).lower()
                            return colors.get(risk_level_str, white_color)
                        if column_name in df_to_process.columns:
                            df_to_process['color'] = df_to_process[column_name].apply(get_building_color)
                            new_layer_args['get_fill_color'] = 'color'
                    else:
                        new_layer_args['get_fill_color'] = BUILDING_COLOR_CONFIG['none']['color']
                
                elif layer_id == 'network' and network_metric and network_range:
                    df_to_process[network_metric] = pd.to_numeric(df_to_process[network_metric], errors='coerce')
                    mask = (df_to_process[network_metric] >= network_range[0]) & (df_to_process[network_metric] <= network_range[1])
                    df_to_process = df_to_process[mask]
                    metric_series = df_to_process[network_metric].dropna()
                    if not metric_series.empty:
                        try:
                            decile_labels = pd.qcut(metric_series, 10, labels=False, duplicates='drop')
                            df_to_process['decile'] = decile_labels
                            def get_rainbow_color(decile):
                                if pd.isna(decile): return [128, 128, 128, 150]
                                norm = decile / 9.0; r = int(255 * (norm * 2)) if norm > 0.5 else 0; g = int(255 * (1 - abs(norm - 0.5) * 2)); b = int(255 * (1 - norm * 2)) if norm < 0.5 else 0
                                return [r, g, b, 150]
                            df_to_process['color'] = df_to_process['decile'].apply(get_rainbow_color)
                            df_to_process['value'] = metric_series; df_to_process['metric'] = network_metric
                        except ValueError:
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
                
                elif layer_id == 'neighbourhoods' and selected_neighbourhoods is not None:
                    df_to_process = df_to_process[df_to_process['NAME'].isin(selected_neighbourhoods)]
                
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

