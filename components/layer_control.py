# components/layer_control.py

from dash import html, dcc
from config import LAYER_CONFIG

LAYER_EMOJIS = {
    "neighbourhoods": "🏘️", "buildings": "🏢", "flooding_toggle": "🌊",
    "network": "🌐", "crime_points": "📍", "crime_heatmap": "🔥",
    "deprivation": "📉", "land_use": "🏞️", "population": "👨‍👩‍👧‍👦",
    "stop_and_search": "👮"
}

def create_layer_control_content():
    """
    Creates the HTML components for the new pill-button layer controls.
    """
    children = []
    
    # --- MODIFIED: Separate crime layers from other toggleable layers ---
    crime_layers = {k: v for k, v in LAYER_CONFIG.items() if k.startswith('crime_')}
    other_layers = {k: v for k, v in LAYER_CONFIG.items() if not k.startswith('crime_')}

    # --- MODIFIED: Create a container for the new buttons ---
    button_container = html.Div(className="layer-button-container", children=[
        html.Button(
            id={'type': 'layer-button', 'index': layer_id},
            className=f"layer-button{' selected' if config.get('visible', False) else ''}",
            n_clicks=0,
            children=[
                html.Img(src=config.get('image', ''), className="layer-button-bg"),
                html.Span(f"{LAYER_EMOJIS.get(layer_id, '')} {config['label']}".strip(), className="layer-button-label")
            ]
        ) for layer_id, config in other_layers.items()
    ])
    children.append(button_container)

    # --- MODIFIED: Keep the original Checklists, but hide them ---
    # These will now act as data stores for the button states.
    hidden_stores = [
        dcc.Checklist(
            id=f"{layer_id}-toggle",
            value=[layer_id] if config.get('visible', False) else [],
            style={'display': 'none'}
        ) for layer_id, config in other_layers.items()
    ]
    children.extend(hidden_stores)

    # --- Handle the special case for crime layers ---
    if crime_layers:
        # A single master button to show/hide the crime radio options
        children.append(html.Button(
            id='crime-master-toggle-btn',
            className="layer-button", # Initially not selected
            n_clicks=0,
            children=[
                html.Img(src="assets/images/crimes.png", className="layer-button-bg"),
                html.Span("🚨 Crimes", className="layer-button-label")
            ],
            style={'marginTop': '10px'}
        ))
        
        # Hidden checklist to store the master toggle state
        children.append(dcc.Checklist(id='crime-master-toggle', value=[], style={'display': 'none'}))

        # The radio items for selecting a specific crime view
        crime_radio_options = [
            {'label': f"{LAYER_EMOJIS.get(layer_id, '')} {config['label']}".strip(), 'value': layer_id}
            for layer_id, config in crime_layers.items()
        ]
        children.append(html.Div(
            id='crime-radio-container',
            style={'display': 'none', 'paddingLeft': '20px', 'marginTop': '10px'},
            children=[
                dcc.RadioItems(
                    options=crime_radio_options,
                    value=next((k for k, v in crime_layers.items() if v.get('visible')), None),
                    id="crime-viz-radio"
                )
            ]
        ))

    return children
