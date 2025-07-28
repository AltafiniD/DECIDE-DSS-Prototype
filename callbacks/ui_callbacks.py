# callbacks/ui_callbacks.py

from dash.dependencies import Input, Output, State

def register_callbacks(app):
    """
    Registers all UI-related callbacks to the Dash app.
    """
    app.clientside_callback(
        "function(n, c) { if (!n) { return window.dash_clientside.no_update; } return c.includes('hidden') ? 'slideover-panel slideover-visible' : 'slideover-panel slideover-hidden'; }",
        Output("slideover-panel", "className"), Input("toggle-slideover-btn", "n_clicks"), State("slideover-panel", "className")
    )
    app.clientside_callback(
        "function(n, c) { if (!n) { return window.dash_clientside.no_update; } return c.includes('hidden') ? 'filter-slide-panel filter-visible' : 'filter-slide-panel filter-hidden'; }",
        Output("filter-slide-panel", "className"), Input("toggle-filters-btn", "n_clicks"), State("filter-slide-panel", "className")
    )
    app.clientside_callback(
        "function(v) { return (v && v.includes('crimes')) ? { 'display': 'block', 'paddingLeft': '20px', 'marginTop': '5px' } : { 'display': 'none' }; }",
        Output('crime-radio-container', 'style'), Input('crimes-master-toggle', 'value')
    )

    # --- NEW: Callback for the map style pop-out menu ---
    app.clientside_callback(
        "function(n, c) { if (!n) { return window.dash_clientside.no_update; } return c.includes('hidden') ? 'map-style-options-container visible' : 'map-style-options-container hidden'; }",
        Output("map-style-options-container", "className"), Input("map-style-main-btn", "n_clicks"), State("map-style-options-container", "className")
    )

    # --- NEW: Callback for the collapsible debug panel ---
    app.clientside_callback(
        "function(n, c) { if (!n) { return window.dash_clientside.no_update; } return c.includes('collapsed') ? 'debug-panel-container expanded' : 'debug-panel-container collapsed'; }",
        Output("debug-panel-container", "className"), Input("debug-panel-header", "n_clicks"), State("debug-panel-container", "className")
    )
