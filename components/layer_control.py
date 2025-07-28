# components/layer_control.py

from dash import html, dcc
from config import LAYER_CONFIG

def create_layer_control_panel():
    """
    Creates the floating panel with a single loading spinner in the header
    and toggles for each data layer.
    """
    toggles = [
        dcc.Checklist(
            options=[{'label': config['label'], 'value': layer_id}],
            value=[layer_id] if config.get('visible', False) else [],
            id=f"{layer_id}-toggle",
            style={'marginBottom': '5px'}
        ) for layer_id, config in LAYER_CONFIG.items()
    ]

    panel = html.Div(
        style={
            "position": "absolute", "top": "150px", "left": "20px", "zIndex": "1",
            "backgroundColor": "rgba(255, 255, 255, 0.9)", "padding": "15px",
            "borderRadius": "8px", "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
            "width": "220px"
        },
        children=[
            html.Div(
                className="layer-panel-header",
                children=[
                    html.H3("Layers", style={"marginTop": 0, "marginBottom": 0}),
                    dcc.Loading(
                        id="layers-loading",
                        type="circle",
                        className="layer-spinner",
                        children=html.Div(id="layers-loading-output")
                    )
                ]
            ),
            *toggles
        ]
    )
    return panel
