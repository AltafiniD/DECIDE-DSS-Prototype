# components/layer_control.py

from dash import html, dcc
from config import LAYER_CONFIG

# --- UPDATED: Added an emoji for the Stop & Search layer ---
LAYER_EMOJIS = {
    "neighbourhoods": "🏘️",
    "buildings": "🏢",
    "flooding_toggle": "🌊",
    "network": "🌐",
    "crime_points": "📍",
    "crime_heatmap": "🔥",
    "deprivation": "📉",
    "land_use": "🏞️",

    "population": "👨‍👩‍👧‍👦",
    "stop_and_search": "👮" # <--- New emoji
}

def create_layer_control_content():
    """
    Creates the HTML components for the layer controls.
    """
    children = []
    crime_layers = {k: v for k, v in LAYER_CONFIG.items() if k.startswith('crime_')}
    other_layers = {k: v for k, v in LAYER_CONFIG.items() if not k.startswith('crime_')}

    for layer_id, config in other_layers.items():
        emoji = LAYER_EMOJIS.get(layer_id, '')
        label = f"{emoji} {config['label']}".strip()
        children.append(dcc.Checklist(
            options=[{'label': label, 'value': layer_id}],
            value=[layer_id] if config.get('visible', False) else [],
            id=f"{layer_id}-toggle",
            style={'marginBottom': '5px'}
        ))

    if crime_layers:
        children.append(dcc.Checklist(
            id='crime-master-toggle',
            options=[{'label': "🚨 Crimes", 'value': 'crimes_on'}],
            value=[],
            style={'fontWeight': 'bold'}
        ))

        crime_radio_options = [
            {'label': f"{LAYER_EMOJIS.get(layer_id, '')} {config['label']}".strip(), 'value': layer_id}
            for layer_id, config in crime_layers.items()
        ]
        children.append(html.Div(
            id='crime-radio-container',
            style={'display': 'none', 'paddingLeft': '20px', 'marginTop': '5px'},
            children=[
                dcc.RadioItems(
                    options=crime_radio_options,
                    value=next((k for k, v in crime_layers.items() if v.get('visible')), None),
                    id="crime-viz-radio"
                )
            ]
        ))

    # The header and the controls are returned as a list of components
    return children
