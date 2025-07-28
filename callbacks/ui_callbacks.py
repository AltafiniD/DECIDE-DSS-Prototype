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
            // On initial load, n_clicks is 0. We don't want to update.
            if (!n_clicks) {
                return window.dash_clientside.no_update;
            }
            // On subsequent clicks, toggle the class.
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

    # Corrected callback for the top-down filter panel
    app.clientside_callback(
        """
        function(n_clicks, current_classname) {
            // On initial load, n_clicks is 0. We don't want to update.
            if (!n_clicks) {
                return window.dash_clientside.no_update;
            }
            // On subsequent clicks, toggle the class.
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
