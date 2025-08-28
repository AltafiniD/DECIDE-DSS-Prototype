# components/combined_controls.py

from dash import html, dcc
# Import the content-creation functions from the original component files
from .layer_control import create_layer_control_content
from .map_style_control import create_map_style_content

def create_combined_panel():
    """
    Creates a single control panel with collapsible sections for Layers and Map Style.
    """
    # Call the functions to get the component layouts
    layers_content = create_layer_control_content()
    map_style_content = create_map_style_content()

    # Assemble the final panel
    panel = html.Div(
        className="control-panel",
        children=[
            # --- Collapsible Layers Section ---
            html.Div(
                className="control-widget",
                children=[
                    html.Button(
                        className="collapsible-header",
                        id="layers-collapse-toggle",
                        n_clicks=0,
                        children=[
                            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                                html.H3("Layers", style={"margin": 0}),
                                dcc.Loading(
                                    id="layers-loading",
                                    type="circle",
                                    className="layer-spinner",
                                    children=html.Div(id="layers-loading-output")
                                )
                            ]),
                            html.Span("▼", className="chevron-icon")
                        ]
                    ),
                    html.Div(
                        id="layers-collapse-content",
                        className="collapsible-content collapsible-content-visible", # Start expanded
                        children=layers_content
                    )
                ]
            ),
            # --- Collapsible Map Style Section ---
            html.Div(
                className="control-widget",
                children=[
                    html.Button(
                        className="collapsible-header",
                        id="style-collapse-toggle",
                        n_clicks=0,
                        children=[
                            html.H3("Map Style", style={"margin": 0}),
                            html.Span("▼", className="chevron-icon")
                        ]
                    ),
                    html.Div(
                        id="style-collapse-content",
                        className="collapsible-content collapsible-content-hidden", # Start collapsed
                        children=map_style_content
                    )
                ]
            )
        ]
    )
    
    return panel
