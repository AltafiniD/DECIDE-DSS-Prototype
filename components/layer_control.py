# components/layer_control.py

from dash import html, dcc
from config import LAYER_CONFIG

def create_layer_control_panel():
    """
    Creates the floating panel with toggles for each data layer,
    grouping crime visualizations into a radio button selector.
    """
    children = []
    crime_layers = {k: v for k, v in LAYER_CONFIG.items() if k.startswith('crime_')}
    other_layers = {k: v for k, v in LAYER_CONFIG.items() if not k.startswith('crime_')}

    for layer_id, config in other_layers.items():
        children.append(dcc.Checklist(
            options=[{'label': config['label'], 'value': layer_id}],
            value=[layer_id] if config.get('visible', False) else [],
            id=f"{layer_id}-toggle",
            style={'marginBottom': '5px'}
        ))

    if crime_layers:
        children.append(html.Hr())
        children.append(html.Label("Crime Visualization", style={'fontWeight': 'bold'}))
        children.append(dcc.RadioItems(
            options=[{'label': config['label'], 'value': layer_id} for layer_id, config in crime_layers.items()],
            value=next((k for k, v in crime_layers.items() if v.get('visible')), None),
            id="crime-viz-radio",
            style={'marginTop': '5px'}
        ))
        children.append(html.Hr())

    # --- UPDATED: Removed inline style and added a className ---
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
