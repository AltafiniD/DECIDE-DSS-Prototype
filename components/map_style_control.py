# components/map_style_control.py

from dash import dcc, html
from config import MAP_STYLES

def create_map_style_panel():
    """
    Creates the pop-out button menu for selecting the map's base style.
    """
    # These buttons will be hidden by default and shown on click
    style_buttons = [
        html.Button(label, id=f"style-btn-{label.lower()}", n_clicks=0, className="map-style-option-btn")
        for label in MAP_STYLES.keys()
    ]

    panel = html.Div(
        id="map-style-container",
        className="map-style-container",
        children=[
            # The main button that is always visible
            html.Button("Map Style", id="map-style-main-btn", n_clicks=0),
            # The container for the options, hidden by default
            html.Div(
                id="map-style-options-container",
                className="map-style-options-container hidden",
                children=style_buttons
            )
        ]
    )
    return panel
