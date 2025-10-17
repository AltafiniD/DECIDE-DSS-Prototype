# callbacks/map_callbacks.py

from dash.dependencies import Input, Output, State
from dash import no_update
import pydeck as pdk
import pandas as pd
import numpy as np
import jenkspy
import re 

# Ensure all necessary configs are imported
from config import (
    INITIAL_VIEW_STATE_CONFIG, LAYER_CONFIG, FLOOD_LAYER_CONFIG, 
    BUILDING_COLOR_CONFIG, FLOOD_HAZARD_COLORS, 
    STOP_AND_SEARCH_COLOR_MAP, CRIME_COLOR_MAP 
)

# --- UTILITY FUNCTION: Converts HEX to RGB list with Alpha ---
def hex_to_rgba(hex_color, alpha=220):
    """
    Converts a hex color string (e.g., '#FF5733') to a list of [R, G, B, A]
    for use in Pydeck.
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        # Expand shorthand form (e.g. '03F' to '0033FF')
        hex_color = ''.join([c*2 for c in hex_color])
    try:
        rgb = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        return rgb + [alpha]
    except ValueError:
        # Fallback to the 'None' color for safety if parsing fails
        return hex_to_rgba(CRIME_COLOR_MAP.get('None', '#A9A9A9'))


# --- UTILITY FUNCTION: Generates a color gradient ---
def get_color_gradient(base_rgb, steps, output_hex=True, light_mix=0.1):
    """
    Generates a color gradient from a lighter mix (white) to the base_rgb (darker).
    
    - light_mix: The starting point of the gradient (e.g., 0.1 for 10% mix of base color).
    - output_hex: True for Plotly (histograms), False for Pydeck (map).
    """
    start_rgb = np.array([255, 255, 255])
    end_rgb = np.array(base_rgb)
    
    # Interpolation steps: Start with 'light_mix' of the base color up to 100%
    t_adjusted = np.linspace(light_mix, 1, steps, endpoint=True) 
    
    # Linear interpolation (Mix = (1-t)*White + t*BaseColor)
    gradient_rgb = [(1 - i) * start_rgb + i * end_rgb for i in t_adjusted]
    
    # Clamp values and convert to int
    gradient_rgb = [np.clip(rgb.astype(int), 0, 255) for rgb in gradient_rgb]

    if output_hex:
        def rgb_to_hex(rgb):
            return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        return [rgb_to_hex(rgb) for rgb in gradient_rgb]
    else:
        # Pydeck colors need an alpha channel, use 220
        return [list(rgb) + [220] for rgb in gradient_rgb]


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
                        
                    # --- CRIME POINTS COLORING & ZOOM SCALING ---
                    if layer_id == 'crime_points':
                        
                        # Handle null values in 'Crime type' for coloring
                        df_to_process['Crime type'] = df_to_process['Crime type'].fillna('None')

                        # Map the crime type to the correct HEX color, then convert to RGBA
                        def get_crime_color(crime_type):
                            hex_color = CRIME_COLOR_MAP.get(crime_type, CRIME_COLOR_MAP['None'])
                            return hex_to_rgba(hex_color)

                        df_to_process['color'] = df_to_process['Crime type'].apply(get_crime_color)
                        new_layer_args['get_fill_color'] = 'color'
                        
                        # Use meters for zoom scaling
                        new_layer_args['radius_units'] = 'meters'
                        # Define a radius in meters
                        new_layer_args['get_radius'] = 30
                    # --- END CRIME POINTS ---
            
            elif layer_id in FLOOD_LAYER_CONFIG:
                # NEW: Granular flood layer handling with hazard levels
                layer_config = FLOOD_LAYER_CONFIG[layer_id]
                hazard_level = layer_config.get('hazard_level')
                hazard_type = layer_config.get('hazard_type')
                layer_config_id = layer_config.get('id')
                
                if flooding_toggle and flood_selection and layer_config_id in flood_selection:
                    should_render = True
                    
                    # Filter dataframe by hazard level from the database
                    if hazard_level and 'hazard_level' in df_to_process.columns:
                        df_to_process = df_to_process[
                            df_to_process['hazard_level'].str.lower() == hazard_level.lower()
                        ]
                    
                    # Apply color based on 'risk' column value if available, otherwise use hazard level
                    if 'risk' in df_to_process.columns and hazard_type in FLOOD_HAZARD_COLORS:
                        def get_flood_risk_color(risk_value):
                            """Map risk value to color with transparency"""
                            risk_str = str(risk_value).lower().strip()
                            color_map = FLOOD_HAZARD_COLORS.get(hazard_type, {})
                            
                            # Try to match risk value to a color
                            if risk_str in color_map:
                                color = list(color_map[risk_str])
                            else:
                                # Fallback to hazard_level color if risk doesn't match
                                color = list(color_map.get(hazard_level, [128, 128, 128, 255]))
                            
                            # Set alpha to 150 for transparency
                            color[3] = 150
                            return color
                        
                        df_to_process['color'] = df_to_process['risk'].apply(get_flood_risk_color)
                        new_layer_args['get_fill_color'] = 'color'
                    else:
                        # Fallback: apply color based on hazard level
                        if hazard_type and hazard_level in FLOOD_HAZARD_COLORS.get(hazard_type, {}):
                            color = list(FLOOD_HAZARD_COLORS[hazard_type][hazard_level])
                            color[3] = 150
                            df_to_process['color'] = [color] * len(df_to_process)
                            new_layer_args['get_fill_color'] = 'color'
            
            elif layer_id in LAYER_CONFIG:
                if toggles_dict.get(layer_id):
                    should_render = True
                    
                    # --- NETWORK OUTLINE LINE WIDTH (CORRECTED PathLayer PARAMETERS) ---
                    if layer_id == 'network_outline':
                        # Base road network: width scales with zoom (unit='meters')
                        new_layer_args['get_width'] = 2.0  # PathLayer uses 'get_width'
                        new_layer_args['width_unit'] = 'meters' # PathLayer uses 'width_unit'
                        new_layer_args['width_scale'] = 1  
                        new_layer_args['width_min_pixels'] = 0.5 
                        if 'width_max_pixels' in new_layer_args:
                            del new_layer_args['width_max_pixels']

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
                                        [240, 249, 33], # Starts yellow
                                        [225, 247, 37],
                                        [203, 247, 56],
                                        [174, 242, 88],
                                        [139, 230, 125],
                                        [101, 212, 150],
                                        [64, 190, 175],
                                        [33, 151, 176],
                                        [14, 107, 140],
                                        [13, 34, 88] # Ends dark blue
                                    ]
                                    
                                    # Map class to color with alpha
                                    color_palette.reverse()
                                    df_to_process['color'] = df_to_process['jenks_class'].apply(
                                        lambda c: color_palette[int(c)] + [180] if pd.notna(c) else [200, 200, 200, 100]
                                    )
                                    new_layer_args['get_fill_color'] = 'color'
                                except Exception as e:
                                    print(f"Error calculating Jenks breaks for population: {e}")
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
                        # --- STOP AND SEARCH COLORING LOGIC ---
                        if sas_time_range and isinstance(sas_time_range, list) and len(sas_time_range) == 2 and sas_month_map:
                            df_to_process['Month_dt'] = pd.to_datetime(df_to_process['Date'], errors='coerce').dt.tz_localize(None)
                            start_month_str, end_month_str = sas_month_map.get(str(sas_time_range[0])), sas_month_map.get(str(sas_time_range[1]))
                            if start_month_str and end_month_str:
                                start_date, end_date = pd.to_datetime(start_month_str), pd.to_datetime(end_month_str)
                                df_to_process = df_to_process[(df_to_process['Month_dt'] >= start_date) & (df_to_process['Month_dt'] <= end_date)]
                        
                        if sas_object_search:
                            df_to_process = df_to_process[df_to_process['Object of search'].isin(sas_object_search)]
                        
                        # Handle null values in 'Object of search' for coloring
                        df_to_process['Object of search'] = df_to_process['Object of search'].fillna('None')

                        # Map the object of search to the correct HEX color, then convert to RGBA
                        def get_sas_color(object_of_search):
                            hex_color = STOP_AND_SEARCH_COLOR_MAP.get(object_of_search, STOP_AND_SEARCH_COLOR_MAP['None'])
                            return hex_to_rgba(hex_color)

                        df_to_process['color'] = df_to_process['Object of search'].apply(get_sas_color)
                        new_layer_args['get_fill_color'] = 'color'
                        
                        # Set radius to scale with zoom
                        new_layer_args['radius_units'] = 'meters' 
                        new_layer_args['get_radius'] = 30 
                        # --- END: STOP AND SEARCH COLORING LOGIC ---
                    
                    # --- NETWORK ANALYSIS COLORING & LINE WIDTH ---
                    elif layer_id == 'network' and network_metric and network_range:
                        if network_metric in df_to_process.columns:
                            df_to_process[network_metric] = pd.to_numeric(df_to_process[network_metric], errors='coerce')
                            mask = (df_to_process[network_metric] >= network_range[0]) & (df_to_process[network_metric] <= network_range[1])
                            df_to_process = df_to_process[mask]
                            metric_series = df_to_process[network_metric].dropna()
                            
                            if not metric_series.empty:
                                try:
                                    # Calculate deciles
                                    decile_labels = pd.qcut(metric_series, 10, labels=False, duplicates='drop')
                                    df_to_process['decile'] = decile_labels
                                    
                                    num_deciles = 10
                                    
                                    # Determine coloring based on metric type
                                    if '_rivers_risk' in network_metric:
                                        base_color = FLOOD_HAZARD_COLORS['rivers_risk']['high'][:3]
                                        decile_colors = get_color_gradient(base_color, steps=num_deciles, output_hex=False)
                                    elif '_sea_risk' in network_metric:
                                        base_color = FLOOD_HAZARD_COLORS['sea_risk']['high'][:3]
                                        decile_colors = get_color_gradient(base_color, steps=num_deciles, output_hex=False)
                                    elif '_surface_risk' in network_metric:
                                        base_color = FLOOD_HAZARD_COLORS['surface_risk']['high'][:3]
                                        decile_colors = get_color_gradient(base_color, steps=num_deciles, output_hex=False)
                                    else:
                                        # Other Network Metrics (NACH, NAIN, NADC): Custom Rainbow scale (Blue=Low, Red=High)
                                        rainbow_hex = [
                                            "#0000d3",  # 0: Dark Blue (Low)
                                            "#003cff",  # 1: Blue
                                            "#008cff",  # 2: Light Blue
                                            '#00ccff',  # 3: Cyan
                                            "#00ebbc",  # 4: Light Cyan/Green
                                            "#00eb0c",  # 5: Green
                                            "#ffd900",  # 6: Yellow
                                            '#ffaa00',  # 7: Orange
                                            '#ff5500',  # 8: Red-Orange
                                            '#cc0000'   # 9: Dark Red (High)
                                        ]
                                        
                                        # Convert hex to RGB list with Alpha [220]
                                        decile_colors = [list(tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))) + [220] for h in rainbow_hex]
                                    
                                    # Apply the colors
                                    df_to_process['color'] = df_to_process['decile'].apply(
                                        lambda d: decile_colors[int(d)] if pd.notna(d) else [128, 128, 128, 150]
                                    )
                                    df_to_process['value'] = metric_series; df_to_process['metric'] = network_metric
                                except (ValueError, IndexError):
                                    df_to_process['color'] = [[128, 128, 128, 150]] * len(df_to_process)
                                
                                # Apply line width for analysis network (CORRECTED PathLayer PARAMETERS)
                                new_layer_args['get_color'] = 'color' 
                                new_layer_args['get_width'] = 5.0 # PathLayer uses 'get_width'
                                new_layer_args['width_unit'] = 'meters'
                                new_layer_args['width_scale'] = 1
                                new_layer_args['width_min_pixels'] = 1 
                                if 'width_max_pixels' in new_layer_args:
                                    del new_layer_args['width_max_pixels']

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