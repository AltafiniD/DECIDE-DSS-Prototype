# callbacks/map_callbacks.py

from dash.dependencies import Input, Output, State
import pydeck as pdk
import copy

from config import INITIAL_VIEW_STATE_CONFIG, LAYER_CONFIG

def register_callbacks(app, all_layers, dataframes):
    """
    Registers all map-related callbacks to the Dash app.
    """
    layer_toggle_inputs = [
        Input(f"{layer_id}-toggle", "value") for layer_id in LAYER_CONFIG
    ]

    @app.callback(
        [
            Output("deck-gl", "data"),
            Output("layers-loading-output", "children")
        ],
        [
            Input("perspective-slider", "value"),
            Input("selected-month-store", "data"),
            *layer_toggle_inputs
        ]
    )
    def update_map_view(pitch, selected_month, *layer_toggles):
        """
        This callback reconstructs the map with the correct layers and view,
        including filtering based on the selected month from the graph.
        """
        visible_layers = []
        layers_to_render = copy.deepcopy(all_layers)

        if selected_month and selected_month != "clear":
            crime_layer = layers_to_render.get('crime')
            if crime_layer:
                original_crime_df = dataframes['crime']
                filtered_df = original_crime_df[original_crime_df['Month'] == selected_month]
                crime_layer.data = filtered_df

        if selected_month == "clear":
            layers_to_render['crime'] = all_layers['crime']

        for i, layer_id in enumerate(LAYER_CONFIG.keys()):
            if layer_toggles[i]:
                visible_layers.append(layers_to_render[layer_id])

        view_config = INITIAL_VIEW_STATE_CONFIG.copy()
        view_config['pitch'] = pitch
        updated_view_state = pdk.ViewState(**view_config, transition_duration=250)

        active_tooltip = None
        for layer in reversed(visible_layers):
            layer_id = layer.id
            layer_config = LAYER_CONFIG.get(layer_id, {})
            tooltip_config = layer_config.get("tooltip")
            if tooltip_config:
                active_tooltip = tooltip_config
                break

        deck = pdk.Deck(
            layers=visible_layers,
            initial_view_state=updated_view_state,
            map_style="mapbox://styles/mapbox/light-v9",
            tooltip=active_tooltip if active_tooltip else True
        )
        
        return [deck.to_json(), None]
