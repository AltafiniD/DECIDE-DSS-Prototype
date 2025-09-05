# layouts/main_layout.py

from dash import html, dcc
import dash_deck
import pydeck as pdk
import pandas as pd
import numpy as np
import math
import os
import copy
import jenkspy

from config import (
    MAPBOX_API_KEY, LAYER_CONFIG, FLOOD_LAYER_CONFIG, BUILDING_COLOR_CONFIG,
    INITIAL_VIEW_STATE_CONFIG, MAP_STYLES, NETWORK_METRICS_EXCLUDE
)
from utils.geojson_loader import process_geojson_features
from utils.colours import get_crime_colour_map
# --- MODIFIED: Import the updated slideover panel function ---
from components.slideover_panel import create_slideover_panel
from components.filter_panel import create_filter_panel
from components.combined_controls import create_combined_panel
from chat.chat_window import create_chat_window
from components.settings import create_settings_modal

def load_data_efficiently(file_path):
    """
    Loads data from Parquet if it exists, otherwise falls back to GeoJSON.
    """
    parquet_path = file_path.replace('.geojson', '.parquet')
    
    if os.path.exists(parquet_path):
        print(f"Loading from fast Parquet file: {parquet_path}")
        return pd.read_parquet(parquet_path)
    else:
        print(f"Loading from GeoJSON file: {file_path}")
        return process_geojson_features(file_path)

def create_layout():
    """
    Creates the main layout and returns the dataframes for the callbacks.
    """
    all_layers = {}
    dataframes = {}

    plotly_crime_colours, pydeck_crime_colours = get_crime_colour_map()

    temp_dir = 'temp'
    all_configs = {**LAYER_CONFIG, **FLOOD_LAYER_CONFIG}
    effective_configs = copy.deepcopy(all_configs)

    for layer_key, config in effective_configs.items():
        if 'file_path' in config:
            original_path = all_configs[layer_key]['file_path']
            temp_path = os.path.join(temp_dir, os.path.basename(original_path))
            if os.path.exists(temp_path):
                print(f"Loading temporary file for '{layer_key}': {temp_path}")
                config['file_path'] = temp_path
    
    unique_file_paths = {v['file_path'] for v in effective_configs.values() if 'file_path' in v}
    loaded_files = {path: load_data_efficiently(path) for path in unique_file_paths}

    # Sanitize data types in loaded dataframes to prevent JSON errors ---
    # This ensures that values used are standard Python floats.
    buildings_path = LAYER_CONFIG['buildings']['file_path']
    if buildings_path in loaded_files and 'height' in loaded_files[buildings_path].columns:
        df = loaded_files[buildings_path]
        df['height'] = pd.to_numeric(df['height'], errors='coerce').astype(float)

    network_path = LAYER_CONFIG['network']['file_path']
    if network_path in loaded_files:
        df = loaded_files[network_path]
        numeric_cols = df.select_dtypes(include=np.number).columns
        for col in numeric_cols:
            if col not in NETWORK_METRICS_EXCLUDE:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)


    for layer_key, config in effective_configs.items():
        if config.get('type') == 'toggle_only': 
            continue

        layer_id = config.get('id', layer_key)
        
        df = loaded_files.get(config.get('file_path'))
        if df is None or df.empty:
            dataframes[layer_id] = pd.DataFrame()
            continue
            
        layer_type_str = None
        layer_args = {'data': df, 'id': layer_id, 'opacity': 0.8, 'pickable': True}
        
        if config.get('type') == 'polygon':
            layer_type_str = "PolygonLayer"
            layer_args.update({'stroked': True, 'get_polygon': 'contour', 'filled': True, 'get_line_width': 20})
            if 'flood' in layer_id:
                 layer_args.update({'stroked': False, 'get_fill_color': config.get('color', [128, 128, 128, 100])})
            elif layer_id == 'buildings':
                layer_args.update({'extruded': True, 'wireframe': True, 'get_elevation': 'height', 'get_fill_color': BUILDING_COLOR_CONFIG['none']['color']})
            elif layer_id == 'neighbourhoods':
                layer_args.update({'extruded': False, 'get_fill_color': '[200, 200, 200, 100]', 'get_line_color': '[84, 84, 84, 200]'})
            elif layer_id == 'land_use':
                if 'landuse_text' in df.columns: df = df[df['landuse_text'] != 'Principle Transport'].copy()
                land_use_color_map = {'Coastal water': [0, 1, 125, 160], 'Inland Water': [146, 203, 251, 160], 'Deciduous woodland': [92, 142, 63, 160], 'Coniferous and undifferentiated woodland': [1, 103, 0, 160], 'Unimproved grassland': [147, 195, 124, 160], 'Open or heath and moor land': [92, 142, 63, 160], 'Coastal dunes': [211, 209, 116, 160], 'Wetlands': [146, 203, 251, 160], 'Low density residential with amenities (suburbs and small villages / hamlets)': [255, 221, 139, 160], 'Medium density residential with high streets and amenities': [255, 204, 88, 160], 'High density residential with retail and commercial sites': [255, 181, 0, 160], 'Urban centres - mainly commercial/retail with residential pockets': [121, 117, 187, 160], 'Retail': [223, 133, 124, 160], 'Retail parks': [2, 1, 215, 160], 'Industrial areas': [71, 0, 89, 160], 'Business parks': [106, 3, 142, 160], 'Mining and spoil areas': [156, 54, 56, 160], 'Amenity': [181, 213, 142, 160], 'Recreational land': [110, 29, 4, 160], 'Transport': [190, 190, 190, 160], 'Community services': [140, 162, 215, 160], 'Large complex buildings various use (travel/recreation/ retail)': [80, 80, 193, 160], 'Agriculture - mixed use': [172, 212, 99, 160], 'Agriculture - mainly crops': [218, 233, 154, 160], 'Farms': [130, 208, 129, 160], 'Orchards': [255, 234, 77, 160], 'Glasshouses': [97, 218, 175, 160]}
                default_color = [128, 128, 128, 120]
                df['color'] = df['landuse_text'].map(land_use_color_map).apply(lambda x: x if isinstance(x, list) else default_color) if 'landuse_text' in df.columns else [default_color] * len(df)
                layer_args.update({'data': df.copy(), 'get_fill_color': 'color', 'stroked': False})
            elif layer_id == 'population':
                df['density'] = pd.to_numeric(df['density'], errors='coerce')
                df_valid_density = df[df['density'].notna() & (df['density'] > 0)].copy()
                df_no_density = df[~df.index.isin(df_valid_density.index)].copy()

                # --- MODIFIED: Increased alpha for more vibrant colors ---
                jenks_colors = [
                    [253, 224, 221, 220], [250, 159, 181, 220], [247, 104, 161, 220],
                    [197, 27, 138, 220], [122, 1, 119, 220]
                ]
                
                if not df_valid_density.empty and df_valid_density['density'].nunique() >= 5:
                    breaks = jenkspy.jenks_breaks(df_valid_density['density'], n_classes=5)
                    df_valid_density['bin'] = pd.cut(df_valid_density['density'], bins=breaks, labels=False, include_lowest=True)
                    df_valid_density['color'] = df_valid_density['bin'].apply(lambda x: jenks_colors[x])
                else:
                    df_valid_density['color'] = [jenks_colors[0]] * len(df_valid_density)

                df_no_density['color'] = [[200, 200, 200, 120]] * len(df_no_density)
                df = pd.concat([df_valid_density, df_no_density])

                layer_args.update({'data': df.copy(), 'get_fill_color': 'color', 'get_line_color': [80, 80, 80, 150], 'stroked': True})
            elif layer_id == 'deprivation':
                df['Percentile'] = pd.to_numeric(df['Percentile'], errors='coerce')
                zero_percent_color, blue_scale = [229, 245, 224], [[237, 248, 251], [208, 226, 242], [179, 205, 233], [140, 180, 223], [101, 155, 213], [62, 130, 203], [31, 105, 185], [8, 81, 156], [8, 64, 129], [8, 48, 107]]
                def get_deprivation_color(p):
                    if pd.isna(p): return [128, 128, 128, 180]
                    if p == 0: return zero_percent_color + [180]
                    if 0 < p < 10: return blue_scale[0] + [180]
                    return blue_scale[min(math.floor(p / 10), 9)] + [180] if p >= 10 else [200, 200, 200, 128]
                df['color'] = df['Percentile'].apply(get_deprivation_color)
                layer_args.update({'extruded': False, 'get_fill_color': 'color', 'get_line_color': [80, 80, 80, 50], 'stroked': True, 'get_line_width': 5})
        
        elif config.get('type') == 'scatterplot':
            layer_type_str = "ScatterplotLayer"
            if layer_id == 'crime_points':
                df['color'] = df['Crime type'].map(pydeck_crime_colours).apply(lambda x: x if isinstance(x, list) else [128, 128, 128, 100])
                layer_args.update({'data': df.copy(), 'get_position': 'coordinates', 'get_radius': 15, 'get_fill_color': 'color'})
            elif layer_id == 'stop_and_search':
                layer_args.update({'get_position': 'coordinates', 'get_radius': 10, 'get_fill_color': [220, 20, 60, 200]})

        elif config.get('type') == 'hexagon':
            layer_type_str = "HexagonLayer"
            layer_args.update({'get_position': 'coordinates', 'radius': 100, 'elevation_scale': 4, 'elevation_range': [0, 1000], 'extruded': True, 'color_range': [[255, 255, 178, 25], [254, 204, 92, 85], [253, 141, 60, 135], [240, 59, 32, 185], [189, 0, 38, 255]]})

        elif config.get('type') == 'linestring':
            layer_type_str = "LineLayer"
            layer_args.update({'get_source_position': 'source_position', 'get_target_position': 'target_position', 'get_color': 'color', 'get_width': 5})

        else:
            continue
            
        dataframes[layer_id] = df
        all_layers[layer_id] = (layer_type_str, layer_args)

    initial_visible_layers = [
        pdk.Layer(layer_type, **args)
        for layer_id, (layer_type, args) in all_layers.items()
        if all_configs.get(layer_id, {}).get('visible', False)
    ]

    initial_view_state = pdk.ViewState(**INITIAL_VIEW_STATE_CONFIG)
    filter_panel_content, crime_month_map, sas_month_map = create_filter_panel(
        dataframes.get('crime_points'), dataframes.get('network'), dataframes.get('deprivation'),
        dataframes.get('buildings'), dataframes.get('land_use'), dataframes.get('neighbourhoods'),
        dataframes.get('stop_and_search')
    )
    initial_map_style = MAP_STYLES['Light']['url']

    layout = html.Div(
        id="main-container",
        children=[
            dcc.Location(id='url', refresh=True),
            dcc.Store(id='selected-neighbourhood-store', data=None),
            dcc.Store(id='month-map-store', data=crime_month_map),
            dcc.Store(id='sas-month-map-store', data=sas_month_map),
            dcc.Store(id='map-update-trigger-store'),
            html.Div(
                dash_deck.DeckGL(
                    id="deck-gl", mapboxKey=MAPBOX_API_KEY,
                    data=pdk.Deck(
                        layers=initial_visible_layers,
                        initial_view_state=initial_view_state,
                        map_style=initial_map_style
                    ).to_json(),
                    tooltip=True, enableEvents=['click']
                ),
                style={"position": "absolute", "top": 0, "left": 0, "width": "100%", "height": "100%"}
            ),
            create_chat_window(),
            html.Div(
                id="filter-panel-wrapper",
                className="filter-wrapper filter-hidden",
                children=[filter_panel_content, html.Button("⌃", id="toggle-filters-handle", n_clicks=0)]
            ),
            html.Div(
                className="bottom-left-controls-container",
                children=[create_combined_panel()]
            ),
            html.Button("🐞", id="toggle-debug-btn", className="toggle-debug-btn"),
            html.Div(
                id="debug-panel",
                className="debug-panel-container debug-hidden",
                children=[dcc.Markdown(id="selection-info-display")]
            ),
            # --- MODIFIED: Call the function without arguments ---
            create_slideover_panel(),
            html.Button("❮", id="toggle-slideover-btn"),
            create_settings_modal()
        ]
    )
    return layout, all_layers, dataframes

