# callbacks/ui_callbacks.py

from dash.dependencies import Input, Output, State, ALL
from dash import no_update, ctx

def register_callbacks(app):
    """
    Registers all UI-related callbacks to the Dash app.
    """
    # --- Callback for the image-based map style selector ---
    @app.callback(
        Output('map-style-radio', 'value'),
        Output({'type': 'map-style-button', 'index': ALL}, 'className'),
        Input({'type': 'map-style-button', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def update_map_style_selection(n_clicks):
        from config import MAP_STYLES # Import inside to avoid circular dependency issues
        
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


    # --- Callback for the right-side widget panel and its handle ---
    app.clientside_callback(
        """
        function(n_clicks, current_classname) {
            if (!n_clicks) {
                return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            }
            const is_hidden = current_classname.includes('slideover-hidden');
            const new_classname = is_hidden
                ? 'slideover-panel slideover-visible'
                : 'slideover-panel slideover-hidden';
            const new_button_text = is_hidden ? '❯' : '❮';
            return [new_classname, new_button_text];
        }
        """,
        Output("slideover-panel", "className"),
        Output("toggle-slideover-btn", "children"),
        Input("toggle-slideover-btn", "n_clicks"),
        State("slideover-panel", "className")
    )

    # --- FIXED: Callback now correctly targets 'filter-slide-panel' and uses correct icons ---
    app.clientside_callback(
        """
        function(n_clicks, current_classname) {
            if (!n_clicks) {
                return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            }
            if (typeof current_classname !== 'string') {
                return ['filter-slide-panel filter-visible', '⌄'];
            }
            const is_hidden = current_classname.includes('filter-hidden');
            const new_classname = is_hidden
                ? 'filter-slide-panel filter-visible'
                : 'filter-slide-panel filter-hidden';
            const new_button_text = is_hidden ? '⌄' : '⌃';
            return [new_classname, new_button_text];
        }
        """,
        Output("filter-slide-panel", "className"),
        Output("toggle-filters-handle", "children"),
        Input("toggle-filters-handle", "n_clicks"),
        State("filter-slide-panel", "className")
    )

    # Callback to show/hide the crime radio buttons
    @app.callback(
        Output('crime-radio-container', 'style'),
        Input('crime-master-toggle', 'value')
    )
    def toggle_crime_radio_buttons(toggle_value):
        return {'display': 'block', 'paddingLeft': '20px', 'marginTop': '5px'} if toggle_value else {'display': 'none'}

    # --- FIXED: Corrected the typo in the Output ID ---
    @app.callback(
        Output('crime-viz-radio', 'value'),
        Input('crime-master-toggle', 'value'),
        prevent_initial_call=True
    )
    def clear_crime_radio_selection(toggle_value):
        return None if not toggle_value else no_update

    # --- Callbacks for collapsible control panel ---
    app.clientside_callback(
        """
        function(n_clicks, current_classname) {
            if (n_clicks === 0) { return window.dash_clientside.no_update; }
            const is_hidden = current_classname.includes('hidden');
            return is_hidden 
                ? 'collapsible-content collapsible-content-visible' 
                : 'collapsible-content collapsible-content-hidden';
        }
        """,
        Output("layers-collapse-content", "className"),
        Input("layers-collapse-toggle", "n_clicks"),
        State("layers-collapse-content", "className")
    )

    app.clientside_callback(
        """
        function(n_clicks, current_classname) {
            if (n_clicks === 0) { return window.dash_clientside.no_update; }
            const is_hidden = current_classname.includes('hidden');
            return is_hidden 
                ? 'collapsible-content collapsible-content-visible' 
                : 'collapsible-content collapsible-content-hidden';
        }
        """,
        Output("style-collapse-content", "className"),
        Input("style-collapse-toggle", "n_clicks"),
        State("style-collapse-content", "className")
    )

    # Clientside callback for the debug panel
    app.clientside_callback(
        """
        function(n_clicks, current_classname) {
            if (!n_clicks) { return window.dash_clientside.no_update; }
            return current_classname.includes('debug-hidden')
                ? 'debug-panel-container debug-visible'
                : 'debug-panel-container debug-hidden';
        }
        """,
        Output("debug-panel", "className"),
        Input("toggle-debug-btn", "n_clicks"),
        State("debug-panel", "className"),
    )

