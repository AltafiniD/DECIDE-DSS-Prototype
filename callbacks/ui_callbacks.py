# callbacks/ui_callbacks.py

from dash.dependencies import Input, Output, State

def register_callbacks(app):
    """
    Registers all UI-related callbacks to the Dash app.
    """
    # Callback for the right-side widget panel
    app.clientside_callback(
        """
        function(n_clicks, current_classname) {
            if (!n_clicks) { return window.dash_clientside.no_update; }
            return current_classname.includes('slideover-hidden') ? 'slideover-panel slideover-visible' : 'slideover-panel slideover-hidden';
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
            return current_classname.includes('filter-hidden') ? 'filter-slide-panel filter-visible' : 'filter-slide-panel filter-hidden';
        }
        """,
        Output("filter-slide-panel", "className"),
        Input("toggle-filters-btn", "n_clicks"),
        State("filter-slide-panel", "className")
    )

    # --- NEW: Callback to show/hide the crime visualization radio buttons ---
    app.clientside_callback(
        """
        function(crime_toggle_value) {
            if (crime_toggle_value && crime_toggle_value.includes('crimes')) {
                return { 'display': 'block', 'paddingLeft': '20px', 'marginTop': '5px' };
            } else {
                return { 'display': 'none' };
            }
        }
        """,
        Output('crime-radio-container', 'style'),
        Input('crimes-master-toggle', 'value')
    )
