# layouts/main_layout.py

from dash import html, dcc
import dash_deck
import pydeck as pdk
import pandas as pd

from config import MAPBOX_API_KEY, LAYER_CONFIG, INITIAL_VIEW_STATE_CONFIG, MAP_STYLES
from utils.geojson_loader import process_geojson_features
from utils.colours import get_crime_colour_map
from components.layer_control import create_layer_control_panel
from components.slideover_panel import create_slideover_panel
from components.filter_panel import create_filter_panel
from components.map_style_control import create_map_style_panel

def create_layout():
    """
    Creates the main layout and returns the dataframes for the callbacks.
    """
    all_layers = {}
    dataframes = {}

    plotly_crime_colours, pydeck_crime_colours = get_crime_colour_map()

    unique_files = {v['file_path']: process_geojson_features(v['file_path']) for v in LAYER_CONFIG.values()}

    for layer_id, config in LAYER_CONFIG.items():
        df = unique_files[config['file_path']]
        dataframes[layer_id] = df
        if df.empty: continue
        
        layer_type = config.get('type')
        layer_args = { 'data': df.copy(), 'id': layer_id, 'opacity': 0.8, 'pickable': True }

        if layer_type == 'polygon':
            layer_args.update({'stroked': True, 'get_polygon': 'contour', 'filled': True, 'get_line_width': 20})
            if layer_id == 'buildings':
                layer_args.update({'extruded': True, 'wireframe': True, 'get_elevation': 'height', 'get_fill_color': '[255, 0, 0]'})
            elif layer_id == 'neighbourhoods':
                layer_args.update({'extruded': False, 'get_fill_color': '[200, 200, 200, 100]', 'get_line_color': '[84, 84, 84, 200]'})
            elif layer_id == 'flooding':
                layer_args.update({'extruded': False, 'get_fill_color': '[0, 255, 255, 120]', 'stroked': False})
            layer = pdk.Layer("PolygonLayer", **layer_args)

        elif layer_type == 'scatterplot':
            df['color'] = df['Crime type'].map(pydeck_crime_colours).apply(lambda x: x if isinstance(x, list) else [128, 128, 128, 100])
            layer_args['data'] = df.copy()
            layer_args.update({'get_position': 'coordinates', 'get_radius': 15, 'get_fill_color': 'color'})
            layer = pdk.Layer("ScatterplotLayer", **layer_args)

        elif layer_type == 'hexagon':
            layer_args.update({'get_position': 'coordinates', 'radius': 100, 'elevation_scale': 4, 'elevation_range': [0, 1000], 'extruded': True, 'color_range': [[255, 255, 178, 25], [254, 204, 92, 85], [253, 141, 60, 135], [240, 59, 32, 185], [189, 0, 38, 255]]})
            layer = pdk.Layer("HexagonLayer", **layer_args)

        elif layer_type == 'linestring':
            layer_args.update({'get_source_position': 'source_position', 'get_target_position': 'target_position', 'get_color': 'color', 'get_width': 5})
            layer = pdk.Layer("LineLayer", **layer_args)
        else: continue
        all_layers[layer_id] = layer
    
    initial_visible_layers = [layer for layer_id, layer in all_layers.items() if LAYER_CONFIG[layer_id].get('visible', False)]
    initial_view_state = pdk.ViewState(**INITIAL_VIEW_STATE_CONFIG)

    filter_panel, month_map = create_filter_panel(dataframes.get('crime_points'), dataframes.get('network'))

    layout = html.Div(
        style={"position": "relative", "width": "100vw", "height": "100vh", "overflow": "hidden"},
        children=[
            dcc.Store(id='selected-neighbourhood-store', data=None),
            dcc.Store(id='month-map-store', data=month_map),
            
            html.Div(dash_deck.DeckGL(id="deck-gl", mapboxKey=MAPBOX_API_KEY, data=pdk.Deck(layers=initial_visible_layers, initial_view_state=initial_view_state, map_style=MAP_STYLES['Light']).to_json(), tooltip=True, enableEvents=['click']), style={"position": "absolute", "top": 0, "left": 0, "width": "100%", "height": "100%"}),
            
            html.Button("Show Filters", id="toggle-filters-btn", className="toggle-filters-btn"),
            filter_panel,
            html.Div(
                className="perspective-panel",
                children=[html.H3("Perspective", style={"marginTop": 0, "marginBottom": "20px"}), dcc.Slider(id='perspective-slider', min=0, max=60, step=1, value=INITIAL_VIEW_STATE_CONFIG['pitch'], marks={0: {'label': '2D'}, 60: {'label': '3D'}}, tooltip={"placement": "bottom", "always_visible": False}, updatemode='mouseup')]
            ),
            
            # --- UPDATED: Wrapped left-side panels in a container ---
            html.Div(
                className="left-controls-container",
                children=[
                    create_layer_control_panel(),
                    create_map_style_panel()
                ]
            ),

            html.Div(id="selection-info-panel", className="selection-info-panel", children=[dcc.Markdown(id="selection-info-display")]),
            html.Button("Show Widgets", id="toggle-slideover-btn", className="toggle-widget-btn"),
            create_slideover_panel(dataframes, plotly_crime_colours)
        ]
    )
    return layout, all_layers, dataframes
