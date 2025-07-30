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
            if (!n_clicks) {
                return window.dash_clientside.no_update;
            }
            if (current_classname.includes('slideover-hidden')) {
                return 'slideover-panel slideover-visible';
            } else {
                return 'slideover-panel slideover-hidden';
            }
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
            if (!n_clicks) {
                return window.dash_clientside.no_update;
            }
            if (current_classname.includes('filter-hidden')) {
                return 'filter-slide-panel filter-visible';
            } else {
                return 'filter-slide-panel filter-hidden';
            }
        }
        """,
        Output("filter-slide-panel", "className"),
        Input("toggle-filters-btn", "n_clicks"),
        State("filter-slide-panel", "className")
    )

    # --- NEW: Callback to show/hide the crime radio buttons ---
    @app.callback(
        Output('crime-radio-container', 'style'),
        Input('crime-master-toggle', 'value')
    )
    def toggle_crime_radio_buttons(toggle_value):
        if toggle_value:
            return {'display': 'block', 'paddingLeft': '20px', 'marginTop': '5px'}
        return {'display': 'none'}

    # --- NEW: Callback to clear radio selection when master toggle is off ---
    @app.callback(
        Output('crime-viz-radio', 'value'),
        Input('crime-master-toggle', 'value'),
        prevent_initial_call=True
    )
    def clear_crime_radio_selection(toggle_value):
        if not toggle_value:
            return None # Clear selection
        return no_update # Keep existing selection when toggled on

    # --- NEW: Clientside callback for the debug panel ---
    app.clientside_callback(
        """
        function(n_clicks, current_classname) {
            if (!n_clicks) {
                return window.dash_clientside.no_update;
            }
            if (current_classname.includes('debug-hidden')) {
                return 'debug-panel-container debug-visible';
            } else {
                return 'debug-panel-container debug-hidden';
            }
        }
        """,
        Output("debug-panel", "className"),
        Input("toggle-debug-btn", "n_clicks"),
        State("debug-panel", "className"),
    )