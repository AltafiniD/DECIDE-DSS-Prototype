# callbacks/map_callbacks.py

from dash.dependencies import Input, Output, State
import pydeck as pdk
import copy
import pandas as pd

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
            # The button is now a primary trigger
            Input("apply-filters-btn", "n_clicks"),
            # These inputs will still trigger the callback instantly
            Input("perspective-slider", "value"),
            Input("selected-month-store", "data"),
            *layer_toggle_inputs
        ],
        [
            # Filter values are now passed as State, not Input
            State("time-filter-slider", "value"),
            State("nain-filter-slider", "value"),
            State("crime-type-filter-dropdown", "value"),
            State("month-map-store", "data")
        ]
    )
    def update_map_view(n_clicks, pitch, selected_month, *args):
        """
        This callback reconstructs the map with the correct layers and view.
        It is triggered by the apply button or other direct interactions.
        """
        # --- Unpack Arguments ---
        num_toggles = len(LAYER_CONFIG)
        # The layer toggles are the first part of *args
        layer_toggles = args[:num_toggles]
        # The states are the second part of *args
        time_range, nain_range, selected_crime_types, month_map = args[num_toggles:]

        visible_layers = []
        layers_to_render = copy.deepcopy(all_layers)

        # --- Apply Global Filters ---
        
        # 1. Crime layer filtering
        crime_layer = layers_to_render.get('crime')
        if crime_layer is not None:
            filtered_crime_df = dataframes['crime'].copy()

            # Apply date range filter
            if time_range and month_map:
                start_month_str = month_map.get(str(time_range[0]))
                end_month_str = month_map.get(str(time_range[1]))
                
                if start_month_str and end_month_str:
                    filtered_crime_df['Month_dt'] = pd.to_datetime(filtered_crime_df['Month'], errors='coerce')
                    start_date = pd.to_datetime(start_month_str)
                    end_date = pd.to_datetime(end_month_str)
                    mask = (filtered_crime_df['Month_dt'] >= start_date) & (filtered_crime_df['Month_dt'] <= end_date)
                    filtered_crime_df = filtered_crime_df[mask]
            
            # Apply crime type filter (if any are selected)
            if selected_crime_types:
                mask = filtered_crime_df['Crime type'].isin(selected_crime_types)
                filtered_crime_df = filtered_crime_df[mask]
            
            crime_layer.data = filtered_crime_df

        # 2. Network layer filtering by NAIN range
        network_layer = layers_to_render.get('network')
        if network_layer is not None and nain_range:
            original_network_df = dataframes['network'].copy()
            original_network_df['NAIN'] = pd.to_numeric(original_network_df['NAIN'], errors='coerce')
            mask = (original_network_df['NAIN'] >= nain_range[0]) & (original_network_df['NAIN'] <= nain_range[1])
            network_layer.data = original_network_df[mask]

        # --- Handle single-month click from widget ---
        if selected_month and selected_month != "clear" and crime_layer is not None:
            current_crime_df = crime_layer.data
            month_filtered_df = current_crime_df[current_crime_df['Month'] == selected_month]
            crime_layer.data = month_filtered_df

        # Determine which layers are visible based on the toggles
        for i, layer_id in enumerate(LAYER_CONFIG.keys()):
            if i < len(layer_toggles) and layer_toggles[i]:
                if layer_id in layers_to_render:
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
