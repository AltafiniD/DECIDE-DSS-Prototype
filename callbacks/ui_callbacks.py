# callbacks/ui_callbacks.py

from dash.dependencies import Input, Output, State

def register_callbacks(app):
    """
    Registers all UI-related callbacks to the Dash app.
    """
    app.clientside_callback(
        """
        function(n_clicks, current_classname) {
            if (n_clicks === undefined || n_clicks === null) {
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
