# components/map_style_control.py

from dash import dcc, html
from config import MAP_STYLES

def create_map_style_content():
    """
    Creates the HTML components for the map style selector.
    """
    # FIXED: Return only the radio items, not the header
    return [
        dcc.RadioItems(
            id='map-style-radio',
            options=[{'label': label, 'value': url} for label, url in MAP_STYLES.items()],
            value=MAP_STYLES['Light'],
            labelStyle={'display': 'block', 'marginBottom': '5px'}
        )
    ]
