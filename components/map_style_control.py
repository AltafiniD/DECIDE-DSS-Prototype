# components/map_style_control.py

from dash import dcc, html
from config import MAP_STYLES

def create_map_style_panel():
    """
    Creates the floating panel for selecting the map's base style.
    """
    # --- UPDATED: Changed className to the shared "control-panel" ---
    panel = html.Div(
        className="control-panel",
        children=[
            html.H3("Map Style", style={"marginTop": 0, "marginBottom": "10px"}),
            dcc.RadioItems(
                id='map-style-radio',
                options=[{'label': label, 'value': url} for label, url in MAP_STYLES.items()],
                value=MAP_STYLES['Light'],
                labelStyle={'display': 'block', 'marginBottom': '5px'}
            )
        ]
    )
    return panel
