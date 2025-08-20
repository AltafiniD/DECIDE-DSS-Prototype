# callbacks/ui_callbacks.py

from dash.dependencies import Input, Output, State
from dash import no_update

def register_callbacks(app):
    """
    Registers all UI-related callbacks to the Dash app.
    """
    # Callback for the right-side widget panel
    app.clientside_callback(
        """
        function(n_clicks, current_classname) {
            if (!n_clicks) { return window.dash_clientside.no_update; }
            return current_classname.includes('slideover-hidden')
                ? 'slideover-panel slideover-visible'
                : 'slideover-panel slideover-hidden';
        }
        """,
        Output("slideover-panel", "className"),
        Input("toggle-slideover-btn", "n_clicks"),
        State("slideover-panel", "className")
    )

    # Callback for the top-down filter panel
    app.clientside_callback(
        """
        function(n_clicks, current_classname) {
            if (!n_clicks) { return window.dash_clientside.no_update; }
            return current_classname.includes('filter-hidden')
                ? 'filter-slide-panel filter-visible'
                : 'filter-slide-panel filter-hidden';
        }
        """,
        Output("filter-slide-panel", "className"),
        Input("toggle-filters-btn", "n_clicks"),
        State("filter-slide-panel", "className")
    )

    # Callback to show/hide the crime radio buttons
    @app.callback(
        Output('crime-radio-container', 'style'),
        Input('crime-master-toggle', 'value')
    )
    def toggle_crime_radio_buttons(toggle_value):
        return {'display': 'block', 'paddingLeft': '20px', 'marginTop': '5px'} if toggle_value else {'display': 'none'}

    # Callback to clear radio selection when master toggle is off
    @app.callback(
        Output('crime-viz-radio', 'value'),
        Input('crime-master-toggle', 'value'),
        prevent_initial_call=True
    )
    def clear_crime_radio_selection(toggle_value):
        return None if not toggle_value else no_update

    # --- NEW: Callbacks for collapsible control panel ---
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
