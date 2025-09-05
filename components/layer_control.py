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
    
    crime_layers = {k: v for k, v in LAYER_CONFIG.items() if k.startswith('crime_')}
    other_layers = {k: v for k, v in LAYER_CONFIG.items() if not k.startswith('crime_')}

    # --- MODIFIED: Create a list to hold all buttons for consistent styling ---
    all_buttons = []
    
    # Add the standard layer buttons to the list
    for layer_id, config in other_layers.items():
        all_buttons.append(html.Button(
            id={'type': 'layer-button', 'index': layer_id},
            className=f"layer-button{' selected' if config.get('visible', False) else ''}",
            n_clicks=0,
            children=[
                 html.Span(f"{LAYER_EMOJIS.get(layer_id, '')} {config['label']}".strip(), className="layer-button-label")
            ]
        ))

    # Add the special crime master button to the same list
    if crime_layers:
        all_buttons.append(html.Button(
            id='crime-master-toggle-btn',
            className="layer-button",
            n_clicks=0,
            children=[
                html.Span("🚨 Crimes", className="layer-button-label")
            ]
            # The inline style={'marginTop': '10px'} is no longer needed
        ))

    # Create the container with all buttons inside it
    button_container = html.Div(className="layer-button-container", children=all_buttons)
    children.append(button_container)

    # --- The rest of the component remains the same ---
    hidden_stores = [
        dcc.Checklist(
            id=f"{layer_id}-toggle",
            value=[layer_id] if config.get('visible', False) else [],
            style={'display': 'none'}
        ) for layer_id, config in other_layers.items()
    ]
    children.extend(hidden_stores)

    if crime_layers:
        children.append(dcc.Checklist(id='crime-master-toggle', value=[], style={'display': 'none'}))
        
        crime_radio_options = [
            {'label': f" {LAYER_EMOJIS.get(layer_id, '')} {config['label']}".strip(), 'value': layer_id}
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

