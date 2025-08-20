# layouts/main_layout.py

from dash import html, dcc
import dash_deck
import pydeck as pdk
import pandas as pd
import math

from config import MAPBOX_API_KEY, LAYER_CONFIG, FLOOD_LAYER_CONFIG, BUILDING_COLOR_CONFIG, INITIAL_VIEW_STATE_CONFIG, MAP_STYLES
from utils.geojson_loader import process_geojson_features
from utils.colours import get_crime_colour_map
from components.slideover_panel import create_slideover_panel
from components.filter_panel import create_filter_panel
from components.combined_controls import create_combined_panel

def create_layout():
    """
    Creates the main layout and returns the dataframes for the callbacks.
    """
    all_layers = {}
    dataframes = {}

    plotly_crime_colours, pydeck_crime_colours = get_crime_colour_map()

    files_to_load = {v['file_path']: v for v in LAYER_CONFIG.values() if 'file_path' in v}
    files_to_load.update({v['file_path']: v for v in FLOOD_LAYER_CONFIG.values()})
    unique_files = {path: process_geojson_features(path) for path in files_to_load}

    for layer_id, config in LAYER_CONFIG.items():
        if config.get('type') == 'toggle_only': continue
        
        df = unique_files[config['file_path']]
        dataframes[layer_id] = df
        if df.empty: continue
        
        layer_type = config.get('type')
        layer_args = { 'data': df.copy(), 'id': config.get('id', layer_id), 'opacity': 0.8, 'pickable': True }

        if layer_type == 'polygon':
            layer_args.update({'stroked': True, 'get_polygon': 'contour', 'filled': True, 'get_line_width': 20})
            
            if layer_id == 'buildings':
                layer_args.update({
                    'extruded': True, 'wireframe': True, 'get_elevation': 'height',
                    'get_fill_color': BUILDING_COLOR_CONFIG['none']['color']
                })
            elif layer_id == 'neighbourhoods':
                layer_args.update({'extruded': False, 'get_fill_color': '[200, 200, 200, 100]', 'get_line_color': '[84, 84, 84, 200]'})
            elif layer_id == 'land_use':
                land_use_color_map = {
                    'Coastal water': [0, 1, 125, 160], 'Inland Water': [146, 203, 251, 160],
                    'Deciduous woodland': [92, 142, 63, 160], 'Coniferous and undifferentiated woodland': [1, 103, 0, 160],
                    'Unimproved grassland': [147, 195, 124, 160], 'Open or heath and moor land': [92, 142, 63, 160],
                    'Coastal dunes': [211, 209, 116, 160], 'Wetlands': [146, 203, 251, 160],
                    'Low density residential with amenities (suburbs and small villages / hamlets)': [255, 221, 139, 160],
                    'Medium density residential with high streets and amenities': [255, 204, 88, 160],
                    'High density residential with retail and commercial sites': [255, 181, 0, 160],
                    'Urban centres - mainly commercial/retail with residential pockets': [121, 117, 187, 160],
                    'Retail': [223, 133, 124, 160], 'Retail parks': [2, 1, 215, 160],
                    'Industrial areas': [71, 0, 89, 160], 'Business parks': [106, 3, 142, 160],
                    'Mining and spoil areas': [156, 54, 56, 160], 'Amenity': [181, 213, 142, 160],
                    'Recreational land': [110, 29, 4, 160], 'Transport': [190, 190, 190, 160],
                    'Principle Transport': [171, 171, 171, 160], 'Community services': [140, 162, 215, 160],
                    'Large complex buildings various use (travel/recreation/ retail)': [80, 80, 193, 160],
                    'Agriculture - mixed use': [172, 212, 99, 160], 'Agriculture - mainly crops': [218, 233, 154],
                    'Farms': [130, 208, 129, 160], 'Orchards': [255, 234, 77, 160], 'Glasshouses': [97, 218, 175, 160],
                }
                default_color = [128, 128, 128, 120]
                if 'landuse_text' in df.columns:
                    df['color'] = df['landuse_text'].map(land_use_color_map).apply(lambda x: x if isinstance(x, list) else default_color)
                else:
                    df['color'] = [default_color] * len(df)
                layer_args['data'] = df.copy()
                layer_args.update({'get_fill_color': 'color', 'stroked': False})
            elif layer_id == 'population':
                df['density'] = pd.to_numeric(df['density'], errors='coerce')
                df_non_zero = df[df['density'] > 0].copy()
                df_zero = df[df['density'] <= 0].copy()
                magenta_scale = [[255, 230, 255], [255, 204, 255], [255, 179, 255], [255, 153, 255], [255, 128, 255], [255, 102, 255], [255, 77, 255], [255, 51, 255], [255, 26, 255], [255, 0, 255]]
                if not df_non_zero.empty:
                    df_non_zero['color_index'] = pd.qcut(df_non_zero['density'], q=10, labels=False, duplicates='drop')
                    df_non_zero['color'] = df_non_zero['color_index'].apply(lambda x: magenta_scale[x] + [150])
                df_zero['color'] = [([255, 255, 255, 150])] * len(df_zero)
                df = pd.concat([df_non_zero, df_zero])
                layer_args['data'] = df.copy()
                layer_args.update({'get_fill_color': 'color', 'get_line_color': [80, 80, 80, 150], 'stroked': True})
            elif layer_id == 'deprivation':
                df['Percentile'] = pd.to_numeric(df['Percentile'], errors='coerce')
                zero_percent_color = [229, 245, 224]
                blue_scale = [[237, 248, 251], [208, 226, 242], [179, 205, 233], [140, 180, 223], [101, 155, 213], [62, 130, 203], [31, 105, 185], [8, 81, 156], [8, 64, 129], [8, 48, 107]]
                def get_deprivation_color(p):
                    if pd.isna(p): return [128, 128, 128, 180]
                    if p == 0: return zero_percent_color + [180]
                    if 0 < p < 10: return blue_scale[0] + [180]
                    if p >= 10:
                        index = min(math.floor(p / 10), 9)
                        return blue_scale[index] + [180]
                    return [200, 200, 200, 128]
                df['color'] = df['Percentile'].apply(get_deprivation_color)
                layer_args.update({'extruded': False, 'get_fill_color': 'color', 'get_line_color': [80, 80, 80, 50], 'stroked': True, 'get_line_width': 5})
            layer = pdk.Layer("PolygonLayer", **layer_args)
        elif layer_type == 'scatterplot':
            if layer_id == 'crime_points':
                df['color'] = df['Crime type'].map(pydeck_crime_colours).apply(lambda x: x if isinstance(x, list) else [128, 128, 128, 100])
                layer_args['data'] = df.copy()
                layer_args.update({'get_position': 'coordinates', 'get_radius': 15, 'get_fill_color': 'color'})
            elif layer_id == 'stop_and_search':
                layer_args.update({'get_position': 'coordinates', 'get_radius': 10, 'get_fill_color': [220, 20, 60, 200]})
            layer = pdk.Layer("ScatterplotLayer", **layer_args)
        elif layer_type == 'hexagon':
            layer_args.update({'get_position': 'coordinates', 'radius': 100, 'elevation_scale': 4, 'elevation_range': [0, 1000], 'extruded': True, 'color_range': [[255, 255, 178, 25], [254, 204, 92, 85], [253, 141, 60, 135], [240, 59, 32, 185], [189, 0, 38, 255]]})
            layer = pdk.Layer("HexagonLayer", **layer_args)
        elif layer_type == 'linestring':
            layer_args.update({'get_source_position': 'source_position', 'get_target_position': 'target_position', 'get_color': 'color', 'get_width': 5})
            layer = pdk.Layer("LineLayer", **layer_args)
        else: continue
        all_layers[layer_id] = layer

    for layer_key, config in FLOOD_LAYER_CONFIG.items():
        df = unique_files[config['file_path']]
        dataframes[config['id']] = df
        if df.empty: continue
        layer = pdk.Layer("PolygonLayer", id=config['id'], data=df, pickable=True, stroked=False, filled=True, get_polygon='contour', get_fill_color=config['color'])
        all_layers[config['id']] = layer
    
    initial_visible_layers = [layer for layer_id, layer in all_layers.items() if LAYER_CONFIG.get(layer_id, {}).get('visible', False)]
    initial_view_state = pdk.ViewState(**INITIAL_VIEW_STATE_CONFIG)

    filter_panel, month_map = create_filter_panel(
        dataframes.get('crime_points'), 
        dataframes.get('network'),
        dataframes.get('deprivation'),
        dataframes.get('buildings')
    )

    initial_map_style = MAP_STYLES['Light']['url']

    layout = html.Div(
        style={"position": "relative", "width": "100vw", "height": "100vh", "overflow": "hidden"},
        children=[
            dcc.Store(id='selected-neighbourhood-store', data=None),
            dcc.Store(id='month-map-store', data=month_map),
            html.Div(dash_deck.DeckGL(id="deck-gl", mapboxKey=MAPBOX_API_KEY, data=pdk.Deck(layers=initial_visible_layers, initial_view_state=initial_view_state, map_style=initial_map_style).to_json(), tooltip=True, enableEvents=['click']), style={"position": "absolute", "top": 0, "left": 0, "width": "100%", "height": "100%"}),
            html.Button("Show Filters", id="toggle-filters-btn", className="toggle-filters-btn"),
            filter_panel,
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
            
            # --- THE FIX IS HERE: The panel now comes BEFORE the button ---
            create_slideover_panel(dataframes, plotly_crime_colours),
            html.Button("❮", id="toggle-slideover-btn"),
        ]
    )
    return layout, all_layers, dataframes
