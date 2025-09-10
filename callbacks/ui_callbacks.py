# callbacks/ui_callbacks.py

from dash.dependencies import Input, Output, State, ALL
# --- MODIFIED: Import ClientsideFunction ---
from dash import no_update, ctx, ClientsideFunction
from config import MAP_STYLES, LAYER_CONFIG

def register_callbacks(app):
    """
    Registers all UI-related callbacks to the Dash app.
    """
    other_layer_ids = [k for k, v in LAYER_CONFIG.items() if not k.startswith('crime_')]
    layer_toggle_inputs = [Input(f"{layer_id}-toggle", "value") for layer_id in other_layer_ids]

    @app.callback(
        Output("map-update-trigger-store", "data"),
        [
            Input("apply-filters-btn", "n_clicks"),
            Input("map-style-radio", "value"),
            Input("crime-viz-radio", "value"),
            *layer_toggle_inputs
        ],
        [
            State("time-filter-slider", "value"),
            State("crime-type-filter-dropdown", "value"),
            State("network-metric-dropdown", "value"),
            State("network-range-slider", "value"),
            State("deprivation-category-dropdown", "value"),
            State("land-use-type-dropdown", "value"),
            State("flood-risk-selector", "value"),
            State("building-color-selector", "value"),
            State("neighbourhood-filter-dropdown", "value"),
            State("sas-object-filter-dropdown", "value"),
            State("sas-time-filter-slider", "value")
        ],
        prevent_initial_call=True
    )
    def aggregate_map_inputs(n_clicks, map_style, crime_viz, *args):
        num_states = 11
        toggle_values = args[:-num_states]
        state_values = args[-num_states:]
        return {
            "map_style": map_style,
            "crime_viz": crime_viz,
            "toggles": toggle_values,
            "states": state_values
        }

    @app.callback(
        Output('map-style-radio', 'value'),
        Output({'type': 'map-style-button', 'index': ALL}, 'className'),
        Input({'type': 'map-style-button', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def update_map_style_selection(n_clicks):
        triggered_id = ctx.triggered_id
        if not triggered_id:
            return no_update, no_update
        selected_style_label = triggered_id['index']
        new_map_url = MAP_STYLES[selected_style_label]['url']
        class_names = [
            f"map-style-button{' selected' if label == selected_style_label else ''}"
            for label in MAP_STYLES.keys()
        ]
        return new_map_url, class_names

    layer_button_outputs = [Output(f"{layer_id}-toggle", "value") for layer_id in other_layer_ids]
    layer_button_states = [State(f"{layer_id}-toggle", "value") for layer_id in other_layer_ids]

    @app.callback(
        [Output({'type': 'layer-button', 'index': layer_id}, 'className') for layer_id in other_layer_ids] + layer_button_outputs,
        [Input({'type': 'layer-button', 'index': layer_id}, 'n_clicks') for layer_id in other_layer_ids],
        layer_button_states,
        prevent_initial_call=True
    )
    def update_layer_selections(*args):
        num_layers = len(other_layer_ids)
        clicks, states = args[:num_layers], args[num_layers:]
        triggered_id = ctx.triggered_id
        if not triggered_id:
            return [no_update] * (2 * num_layers)

        clicked_layer_id = triggered_id['index']
        clicked_idx = other_layer_ids.index(clicked_layer_id)
        new_values = list(states)

        is_network_click = clicked_layer_id == 'network'
        is_outline_click = clicked_layer_id == 'network_outline'

        if is_network_click or is_outline_click:
            network_idx = other_layer_ids.index('network') if 'network' in other_layer_ids else -1
            outline_idx = other_layer_ids.index('network_outline') if 'network_outline' in other_layer_ids else -1
            
            is_turning_on = not states[clicked_idx]

            if is_turning_on:
                new_values[clicked_idx] = [clicked_layer_id]
                if is_network_click and outline_idx != -1:
                    new_values[outline_idx] = []
                elif is_outline_click and network_idx != -1:
                    new_values[network_idx] = []
            else:
                new_values[clicked_idx] = []
        else:
            new_values[clicked_idx] = [clicked_layer_id] if not states[clicked_idx] else []
            
        new_classnames = [f"layer-button{' selected' if val else ''}" for val in new_values]
        return new_classnames + new_values

    @app.callback(
        Output('crime-master-toggle', 'value'),
        Output('crime-master-toggle-btn', 'className'),
        Output('crime-radio-container', 'style'),
        Input('crime-master-toggle-btn', 'n_clicks'),
        State('crime-master-toggle', 'value'),
        prevent_initial_call=True
    )
    def toggle_crime_layers(n_clicks, current_value):
        if not current_value:
            new_value = ['crimes_on']
            className = 'layer-button selected'
            style = {'display': 'block', 'paddingLeft': '20px', 'marginTop': '10px'}
        else:
            new_value = []
            className = 'layer-button'
            style = {'display': 'none', 'paddingLeft': '20px', 'marginTop': '10px'}
        return new_value, className, style

    @app.callback(
        Output('crime-viz-radio', 'value'),
        Input('crime-master-toggle', 'value'),
        prevent_initial_call=True
    )
    def clear_crime_radio_selection(toggle_value):
        return None if not toggle_value else no_update

    @app.callback(
        Output('settings-modal-overlay', 'className'),
        Output('main-container', 'className'),
        [Input('settings-btn', 'n_clicks'),
         Input('settings-modal-close-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def toggle_settings_modal(open_clicks, close_clicks):
        if ctx.triggered_id == 'settings-btn':
            return 'settings-modal-overlay-visible', 'blurred'
        return 'settings-modal-overlay-hidden', ''

    # --- MODIFIED: All clientside JS moved to assets/scripts.js ---
    app.clientside_callback(
        ClientsideFunction(namespace='ui_callbacks', function_name='initChatHover'),
        Output('chat-window-container', 'data-hover-setup'),
        Input('chat-window-container', 'id')
    )

    app.clientside_callback(
        """
        function(n_clicks, current_className) {
            if (!n_clicks) {
                return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            }
            const is_hidden = current_className.includes('hidden');
            const new_className = is_hidden ? 'slideover-panel slideover-visible' : 'slideover-panel slideover-hidden';
            const new_button_text = is_hidden ? '❯' : '❮';
            return [new_className, new_button_text];
        }
        """,
        Output("slideover-panel", "className"),
        Output("toggle-slideover-btn", "children"),
        Input("toggle-slideover-btn", "n_clicks"),
        State("slideover-panel", "className")
    )

    app.clientside_callback(
        """
        function(n_clicks, current_className) {
            if (!n_clicks) {
                return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            }
            if (typeof current_className !== 'string') {
                return ['filter-wrapper filter-visible', '⌄'];
            }
            const is_hidden = current_className.includes('hidden');
            const new_className = is_hidden ? 'filter-wrapper filter-visible' : 'filter-wrapper filter-hidden';
            const new_button_text = is_hidden ? '⌄' : '⌃';
            return [new_className, new_button_text];
        }
        """,
        Output("filter-panel-wrapper", "className"),
        Output("toggle-filters-handle", "children"),
        Input("toggle-filters-handle", "n_clicks"),
        State("filter-panel-wrapper", "className")
    )

    app.clientside_callback(
        """
        function(n_clicks, current_className) {
            if (n_clicks === 0) {
                return window.dash_clientside.no_update;
            }
            const is_hidden = current_className.includes('hidden');
            return is_hidden ? 'collapsible-content collapsible-content-visible' : 'collapsible-content collapsible-content-hidden';
        }
        """,
        Output("layers-collapse-content", "className"),
        Input("layers-collapse-toggle", "n_clicks"),
        State("layers-collapse-content", "className")
    )

    app.clientside_callback(
        """
        function(n_clicks, current_className) {
            if (n_clicks === 0) {
                return window.dash_clientside.no_update;
            }
            const is_hidden = current_className.includes('hidden');
            return is_hidden ? 'collapsible-content collapsible-content-visible' : 'collapsible-content collapsible-content-hidden';
        }
        """,
        Output("style-collapse-content", "className"),
        Input("style-collapse-toggle", "n_clicks"),
        State("style-collapse-content", "className")
    )

    app.clientside_callback(
        """
        function(n_clicks, current_className) {
            if (!n_clicks) {
                return window.dash_clientside.no_update;
            }
            return current_className.includes('debug-hidden') ? 'debug-panel-container debug-visible' : 'debug-panel-container debug-hidden';
        }
        """,
        Output("debug-panel", "className"),
        Input("toggle-debug-btn", "n_clicks"),
        State("debug-panel", "className")
    )

    app.clientside_callback(
        ClientsideFunction(namespace='ui_callbacks', function_name='scrollChat'),
        Output('chat-history', 'data-scroll-version'),
        Input('chat-history', 'children'),
        prevent_initial_call=True
    )


