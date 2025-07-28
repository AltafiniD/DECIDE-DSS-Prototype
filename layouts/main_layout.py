# layouts/main_layout.py

from dash import html, dcc
import dash_deck
import pydeck as pdk
import pandas as pd

from config import MAPBOX_API_KEY, LAYER_CONFIG, INITIAL_VIEW_STATE_CONFIG
from utils.geojson_loader import process_geojson_features
from utils.colours import get_crime_colour_map
from components.layer_control import create_layer_control_panel
from components.slideover_panel import create_slideover_panel
from components.top_bar import create_top_bar # Import the new top bar

def create_layout():
    """
    Creates the main layout and returns the dataframes for the callbacks.
    """
    all_layers = {}
    dataframes = {}

    plotly_crime_colours, pydeck_crime_colours = get_crime_colour_map()

    for layer_id, config in LAYER_CONFIG.items():
        df = process_geojson_features(config['file_path'])
        dataframes[layer_id] = df
        if df.empty: continue
        
        layer_type = config.get('type')
        layer_args = { 'data': df, 'id': layer_id, 'opacity': 0.8, 'pickable': True }
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
            layer_args.update({'get_position': 'coordinates', 'get_radius': 15, 'get_fill_color': 'color'})
            layer = pdk.Layer("ScatterplotLayer", **layer_args)
        elif layer_type == 'linestring':
            nain_min, nain_max = 0.2, 0.9
            def get_rainbow_color(value):
                if pd.isna(value): return [128, 128, 128, 100]
                norm = max(0, min(1, (value - nain_min) / (nain_max - nain_min)))
                r = int(255 * (norm * 2)) if norm > 0.5 else 0; g = int(255 * (1 - abs(norm - 0.5) * 2)); b = int(255 * (1 - norm * 2)) if norm < 0.5 else 0
                return [r, g, b, 150]
            df['color'] = df['NAIN'].apply(get_rainbow_color)
            layer_args.update({'get_source_position': 'source_position', 'get_target_position': 'target_position', 'get_color': 'color', 'get_width': 5})
            layer = pdk.Layer("LineLayer", **layer_args)
        else: continue
        all_layers[layer_id] = layer
    
    initial_visible_layers = [layer for layer_id, layer in all_layers.items() if LAYER_CONFIG[layer_id].get('visible', False)]
    initial_view_state = pdk.ViewState(**INITIAL_VIEW_STATE_CONFIG)

    top_bar, month_map = create_top_bar(dataframes.get('crime', pd.DataFrame()), dataframes.get('network', pd.DataFrame()))

    layout = html.Div(
        className="main-container",
        children=[
            dcc.Store(id='selected-neighbourhood-store', data=None),
            dcc.Store(id='selected-month-store', data=None),
            dcc.Store(id='month-map-store', data=month_map),
            
            top_bar, # The new top bar is placed here

            html.Div(
                className="map-container",
                children=[
                    dash_deck.DeckGL(
                        id="deck-gl", mapboxKey=MAPBOX_API_KEY,
                        data=pdk.Deck(layers=initial_visible_layers, initial_view_state=initial_view_state, map_style="mapbox://styles/mapbox/light-v9").to_json(),
                        tooltip=True, enableEvents=['click']
                    ),
                    # All floating panels are now children of the map container
                    html.Div(
                        className="perspective-panel",
                        children=[
                            html.H3("Perspective", style={"marginTop": 0, "marginBottom": "20px"}),
                            dcc.Slider(
                                id='perspective-slider', min=0, max=60, step=1, value=INITIAL_VIEW_STATE_CONFIG['pitch'],
                                marks={0: {'label': '2D'}, 60: {'label': '3D'}},
                                tooltip={"placement": "bottom", "always_visible": False}, updatemode='mouseup'
                            )
                        ]
                    ),
                    create_layer_control_panel(),
                    html.Div(id="selection-info-panel", className="selection-info-panel", children=[dcc.Markdown(id="selection-info-display")]),
                    html.Button("Show Widgets", id="toggle-slideover-btn", className="toggle-widget-btn"),
                    create_slideover_panel(dataframes, plotly_crime_colours)
                ]
            )
        ]
    )
    return layout, all_layers, dataframes
