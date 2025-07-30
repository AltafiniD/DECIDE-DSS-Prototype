# components/layer_control.py

from dash import html, dcc
from config import LAYER_CONFIG

# --- NEW: Emojis for layers ---
LAYER_EMOJIS = {
    "neighbourhoods": "🏘️",
    "buildings": "🏢",
    "flooding": "🌊",
    "network": "🌐",
    "crime_points": "📍",
    "crime_heatmap": "🔥"
}

def create_layer_control_panel():
    """
    Creates the floating panel with toggles for each data layer,
    grouping crime visualizations into a master toggle and radio selector.
    """
    children = []
    crime_layers = {k: v for k, v in LAYER_CONFIG.items() if k.startswith('crime_')}
    other_layers = {k: v for k, v in LAYER_CONFIG.items() if not k.startswith('crime_')}

    # --- UPDATED: Add toggles for non-crime layers with emojis ---
    for layer_id, config in other_layers.items():
        emoji = LAYER_EMOJIS.get(layer_id, '')
        label = f"{emoji} {config['label']}".strip()
        children.append(dcc.Checklist(
            options=[{'label': label, 'value': layer_id}],
            value=[layer_id] if config.get('visible', False) else [],
            id=f"{layer_id}-toggle",
            style={'marginBottom': '5px'}
        ))

    # --- UPDATED: Crime layers are now controlled by a master toggle ---
    if crime_layers:
        children.append(html.Hr())
        
        # Master toggle for all crime visualizations
        children.append(dcc.Checklist(
            id='crime-master-toggle',
            options=[{'label': "🚨 Crimes", 'value': 'crimes_on'}],
            value=[],
            style={'fontWeight': 'bold'}
        ))

        # Radio buttons for selecting the crime viz, hidden by default
        crime_radio_options = [
            {'label': f"{LAYER_EMOJIS.get(layer_id, '')} {config['label']}".strip(), 'value': layer_id}
            for layer_id, config in crime_layers.items()
        ]
        children.append(html.Div(
            id='crime-radio-container',
            style={'display': 'none', 'paddingLeft': '20px', 'marginTop': '5px'}, # Indented and hidden
            children=[
                dcc.RadioItems(
                    options=crime_radio_options,
                    value=next((k for k, v in crime_layers.items() if v.get('visible')), None),
                    id="crime-viz-radio"
                )
            ]
        ))
        children.append(html.Hr())

    panel = html.Div(
        className="control-panel",
        children=[
            html.Div(
                className="layer-panel-header",
                children=[
                    html.H3("Layers", style={"marginTop": 0, "marginBottom": 0}),
                    dcc.Loading(id="layers-loading", type="circle", className="layer-spinner", children=html.Div(id="layers-loading-output"))
                ]
            ),
            *children
        ]
    )
    return panel