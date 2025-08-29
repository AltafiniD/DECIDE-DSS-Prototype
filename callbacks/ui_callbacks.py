# callbacks/ui_callbacks.py

from dash.dependencies import Input, Output, State, ALL
from dash import no_update, ctx
from config import MAP_STYLES, LAYER_CONFIG

def register_callbacks(app):
    """
    Registers all UI-related callbacks to the Dash app.
    """
    # This callback aggregates all map-related inputs into a single store.
    # This store then becomes the single trigger for the expensive map update callback.
    other_layer_ids = [k for k, v in LAYER_CONFIG.items() if not k.startswith('crime_') and v.get('type') != 'toggle_only']
    layer_toggle_inputs = [Input("flooding_toggle-toggle", "value")] + [Input(f"{layer_id}-toggle", "value") for layer_id in other_layer_ids]

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
            State("building-color-selector", "value")
        ],
        prevent_initial_call=True
    )
    def aggregate_map_inputs(n_clicks, map_style, crime_viz, *args):
        # This callback runs instantly when any input changes.
        # It bundles all the current settings into a dictionary.
        num_states = 8
        toggle_values = args[:-num_states]
        state_values = args[-num_states:]
        
        return {
            "map_style": map_style,
            "crime_viz": crime_viz,
            "toggles": toggle_values,
            "states": state_values
        }

    # --- Map style selector callback (unchanged) ---
    @app.callback(
        Output('map-style-radio', 'value'),
        Output({'type': 'map-style-button', 'index': ALL}, 'className'),
        Input({'type': 'map-style-button', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def update_map_style_selection(n_clicks):
        triggered_id = ctx.triggered_id
        if not triggered_id: return no_update, no_update
        selected_style_label = triggered_id['index']
        new_map_url = MAP_STYLES[selected_style_label]['url']
        class_names = [f"map-style-button{' selected' if label == selected_style_label else ''}" for label in MAP_STYLES.keys()]
        return new_map_url, class_names

    # --- Layer pill-buttons callback (unchanged) ---
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
        clicks = args[:num_layers]
        states = args[num_layers:]
        
        triggered_id = ctx.triggered_id
        if not triggered_id:
            return [no_update] * (2 * num_layers)

        clicked_layer_id = triggered_id['index']
        clicked_idx = other_layer_ids.index(clicked_layer_id)

        new_values = list(states)
        new_values[clicked_idx] = [clicked_layer_id] if not states[clicked_idx] else []

        new_classnames = [f"layer-button{' selected' if val else ''}" for val in new_values]
        
        return new_classnames + new_values

    # --- Master crime button callback (unchanged) ---
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

    # --- Clear crime radio selection callback (unchanged) ---
    @app.callback(
        Output('crime-viz-radio', 'value'),
        Input('crime-master-toggle', 'value'),
        prevent_initial_call=True
    )
    def clear_crime_radio_selection(toggle_value):
        return None if not toggle_value else no_update

    # --- Clientside callback for chat window hover effect ---
    app.clientside_callback(
        """
        function(_) {
            // This ensures the setup runs only once after the component is on the page
            if (window.chatHoverInitialized) {
                return window.dash_clientside.no_update;
            }
            window.chatHoverInitialized = true;

            const chatWindow = document.getElementById('chat-window-container');
            if (!chatWindow) return '';

            let timeoutId = null;

            const activateChat = () => {
                clearTimeout(timeoutId);
                chatWindow.classList.add('chat-active');
            };

            const deactivateChat = () => {
                timeoutId = setTimeout(() => {
                    chatWindow.classList.remove('chat-active');
                }, 5000); // 5 seconds
            };

            chatWindow.addEventListener('mouseenter', activateChat);
            chatWindow.addEventListener('mouseleave', deactivateChat);
            
            // Initially activate and then set a timer to deactivate
            activateChat();
            deactivateChat();

            return ''; // No output needed, just setting up listeners
        }
        """,
        Output('chat-window-container', 'data-hover-setup'), # Use a dummy data-* attribute
        Input('chat-window-container', 'id')
    )


    # --- Existing clientside callbacks for panels (unchanged) ---
    app.clientside_callback(
        "function(n,c){if(!n)return[window.dash_clientside.no_update,window.dash_clientside.no_update];const i=c.includes('hidden');return[i?'slideover-panel slideover-visible':'slideover-panel slideover-hidden',i?'❯':'❮']}",
        Output("slideover-panel", "className"), Output("toggle-slideover-btn", "children"),
        Input("toggle-slideover-btn", "n_clicks"), State("slideover-panel", "className")
    )
    app.clientside_callback(
        "function(n,c){if(!n)return[window.dash_clientside.no_update,window.dash_clientside.no_update];if(typeof c!=='string')return['filter-wrapper filter-visible','⌄'];const i=c.includes('hidden');return[i?'filter-wrapper filter-visible':'filter-wrapper filter-hidden',i?'⌄':'⌃']}",
        Output("filter-panel-wrapper", "className"), Output("toggle-filters-handle", "children"),
        Input("toggle-filters-handle", "n_clicks"), State("filter-panel-wrapper", "className")
    )
    app.clientside_callback(
        "function(n,c){if(n===0)return window.dash_clientside.no_update;const i=c.includes('hidden');return i?'collapsible-content collapsible-content-visible':'collapsible-content collapsible-content-hidden'}",
        Output("layers-collapse-content", "className"), Input("layers-collapse-toggle", "n_clicks"), State("layers-collapse-content", "className")
    )
    app.clientside_callback(
        "function(n,c){if(n===0)return window.dash_clientside.no_update;const i=c.includes('hidden');return i?'collapsible-content collapsible-content-visible':'collapsible-content collapsible-content-hidden'}",
        Output("style-collapse-content", "className"), Input("style-collapse-toggle", "n_clicks"), State("style-collapse-content", "className")
    )
    app.clientside_callback(
        "function(n,c){if(!n)return window.dash_clientside.no_update;return c.includes('debug-hidden')?'debug-panel-container debug-visible':'debug-panel-container debug-hidden'}",
        Output("debug-panel", "className"), Input("toggle-debug-btn", "n_clicks"), State("debug-panel", "className")
    )
