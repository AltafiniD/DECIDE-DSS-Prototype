# layouts/main_layout.py

from dash import html, dcc
import dash_deck
import pydeck as pdk
import pandas as pd

from config import MAPBOX_API_KEY, LAYER_CONFIG, INITIAL_VIEW_STATE_CONFIG, MAP_STYLES
from utils.cache import get_dataframe
from utils.colours import get_crime_colour_map
from components.layer_control import create_layer_control_panel
from components.slideover_panel import create_slideover_panel
from components.filter_panel import create_filter_panel
from components.map_style_control import create_map_style_panel

def create_layout():
    """
    Creates the main layout. Stores layer configurations instead of instantiated objects.
    """
    all_layers_config = {}
    plotly_crime_colours, pydeck_crime_colours = get_crime_colour_map()

    for layer_id, config in LAYER_CONFIG.items():
        # This will still lazy-load data for initially visible layers, but now that's none.
        df = get_dataframe(layer_id)
        
        if df.empty:
            print(f"Skipping initial creation of layer '{layer_id}' due to empty dataframe.")

        layer_type_str = None
        layer_args = { 'data': df, 'id': layer_id, 'opacity': 0.8, 'pickable': True }

        if config.get('type') == 'polygon':
            layer_type_str = "PolygonLayer"
            layer_args.update({'stroked': True, 'get_polygon': 'contour', 'filled': True, 'get_line_width': 20})
            if layer_id == 'buildings':
                layer_args.update({'extruded': True, 'wireframe': True, 'get_elevation': 'height', 'get_fill_color': '[255, 0, 0]'})
            elif layer_id == 'neighbourhoods':
                layer_args.update({'extruded': False, 'get_fill_color': '[200, 200, 200, 100]', 'get_line_color': '[84, 84, 84, 200]'})
            elif layer_id == 'flooding':
                layer_args.update({'extruded': False, 'get_fill_color': '[0, 255, 255, 120]', 'stroked': False})

        elif config.get('type') == 'scatterplot':
            layer_type_str = "ScatterplotLayer"
            df['colour'] = df['Crime type'].map(pydeck_crime_colours).apply(lambda x: x if isinstance(x, list) else [128, 128, 128, 100])
            layer_args['data'] = df
            layer_args.update({'get_position': 'coordinates', 'get_radius': 15, 'get_fill_color': 'colour'})

        elif config.get('type') == 'hexagon':
            layer_type_str = "HexagonLayer"
            layer_args.update({'get_position': 'coordinates', 'radius': 100, 'elevation_scale': 4, 'elevation_range': [0, 1000], 'extruded': True, 'color_range': [[255, 255, 178, 25], [254, 204, 92, 85], [253, 141, 60, 135], [240, 59, 32, 185], [189, 0, 38, 255]]})

        elif config.get('type') == 'linestring':
            layer_type_str = "LineLayer"
            layer_args.update({'get_source_position': 'source_position', 'get_target_position': 'target_position', 'get_color': [128, 128, 128, 100], 'get_width': 5})
        
        if layer_type_str:
            all_layers_config[layer_id] = {"type": layer_type_str, "args": layer_args}

    initial_visible_layers = [
        pdk.Layer(config['type'], **config['args'])
        for layer_id, config in all_layers_config.items()
        if LAYER_CONFIG[layer_id].get('visible', False) and not config['args']['data'].empty
    ]
    
    initial_view_state = pdk.ViewState(**INITIAL_VIEW_STATE_CONFIG)
    
    # THE FIX: Only pass the crime dataframe, which is smaller and needed for the time slider.
    crime_df_initial = get_dataframe('crime_points')
    filter_panel, month_map = create_filter_panel(crime_df_initial)
    
    # We still need the network_df for the slideover panel, but this is okay as it's
    # only loaded when the app starts, and the panel itself isn't visible.
    network_df_initial = get_dataframe('network')

    layout = html.Div(
        style={"position": "relative", "width": "100vw", "height": "100vh", "overflow": "hidden"},
        children=[
            dcc.Store(id='selected-neighbourhood-store', data=None),
            dcc.Store(id='month-map-store', data=month_map),
            html.Div(dash_deck.DeckGL(id="deck-gl", mapboxKey=MAPBOX_API_KEY, data=pdk.Deck(layers=initial_visible_layers, initial_view_state=initial_view_state, map_style=MAP_STYLES['Light']).to_json(), tooltip=True, enableEvents=['click']), style={"position": "absolute", "top": 0, "left": 0, "width": "100%", "height": "100%"}),
            
            html.Button("Show Filters", id="toggle-filters-btn", className="toggle-filters-btn"),
            filter_panel,

            html.Div(className="bottom-left-controls", children=[
                create_layer_control_panel(),
                create_map_style_panel(),
            ]),
            
            html.Div(
                id="debug-panel-container",
                className="debug-panel-container collapsed",
                children=[
                    html.Div(id="debug-panel-header", children="Debug"),
                    html.Div(id="selection-info-panel", className="info-panel", children=[dcc.Markdown(id="selection-info-display")])
                ]
            ),
            
            html.Button("Show Widgets", id="toggle-slideover-btn", className="toggle-widget-btn"),
            create_slideover_panel(
                {'crime_points': crime_df_initial, 'network': network_df_initial},
                plotly_crime_colours
            )
        ]
    )
    return layout, all_layers_config
