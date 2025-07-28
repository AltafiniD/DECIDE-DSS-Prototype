# components/layer_control.py

from dash import html, dcc
from config import LAYER_CONFIG

def create_layer_control_panel():
    """
    Creates the floating panel with a conditional crime visualization selector.
    """
    children = []
    # Separate the crime layers from the others
    crime_layers = {k: v for k, v in LAYER_CONFIG.items() if k.startswith('crime_')}
    other_layers = {k: v for k, v in LAYER_CONFIG.items() if not k.startswith('crime_')}

    # Create standard checklists for non-crime layers
    for layer_id, config in other_layers.items():
        children.append(dcc.Checklist(
            options=[{'label': config['label'], 'value': layer_id}],
            value=[layer_id] if config.get('visible', False) else [],
            id=f"{layer_id}-toggle",
            style={'marginBottom': '5px'}
        ))

    # --- UPDATED: Conditional Crime Layer Selector ---
    if crime_layers:
        children.append(html.Hr())
        # The master checkbox for all crime visualizations
        children.append(dcc.Checklist(
            options=[{'label': 'Crimes', 'value': 'crimes'}],
            value=['crimes'] if any(c.get('visible') for c in crime_layers.values()) else [],
            id='crimes-master-toggle',
            style={'fontWeight': 'bold'}
        ))
        # The radio buttons, hidden by default
        children.append(html.Div(
            id='crime-radio-container',
            style={'paddingLeft': '20px', 'marginTop': '5px'}, # Indent for clarity
            children=[
                dcc.RadioItems(
                    options=[{'label': config['label'], 'value': layer_id} for layer_id, config in crime_layers.items()],
                    value=next((k for k, v in crime_layers.items() if v.get('visible')), None),
                    id="crime-viz-radio",
                    labelStyle={'display': 'block', 'marginBottom': '5px'}
                )
            ]
        ))
        children.append(html.Hr())

    panel = html.Div(
        className="info-panel",
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
