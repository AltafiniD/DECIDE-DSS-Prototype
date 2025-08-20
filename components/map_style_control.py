# components/map_style_control.py

from dash import dcc, html
from config import MAP_STYLES

def create_map_style_content():
    """
    Creates the HTML components for the new image-based map style selector.
    """
    # Create a button for each map style
    style_buttons = [
        html.Button(
            id={'type': 'map-style-button', 'index': label},
            className=f"map-style-button{' selected' if label == 'Light' else ''}",
            n_clicks=0,
            children=[
                html.Img(src=config['image'], className="map-style-image"),
                html.Span(label, className="map-style-label")
            ]
        ) for label, config in MAP_STYLES.items()
    ]

    # The main container for the 2x2 grid
    grid_container = html.Div(
        className="map-style-grid",
        children=style_buttons
    )

    # A hidden radio item component to store the actual map URL value.
    # This is what the map callback will listen to, so we don't need to change it.
    hidden_radio_items = dcc.RadioItems(
        id='map-style-radio',
        options=[{'label': label, 'value': config['url']} for label, config in MAP_STYLES.items()],
        value=MAP_STYLES['Light']['url'],
        style={'display': 'none'} # This component is not visible to the user
    )

    return [grid_container, hidden_radio_items]
