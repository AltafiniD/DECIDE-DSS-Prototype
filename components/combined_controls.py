# components/combined_controls.py

from dash import html
# Import the content-creation functions from the original component files
from .layer_control import create_layer_control_content
from .map_style_control import create_map_style_content

def create_combined_panel():
    """
    Creates a single control panel by calling the content-creation functions
    from the layer and map style component files and wrapping each in a widget-like container.
    """
    # Call the functions to get the component layouts
    layers_content = create_layer_control_content()
    map_style_content = create_map_style_content()

    # Assemble the final panel
    panel = html.Div(
        className="control-panel",
        children=[
            # The content for the layers section, wrapped in a styled container
            html.Div(
                className="control-widget",
                children=layers_content
            ),
            # The content for the map style section, wrapped in a styled container
            html.Div(
                className="control-widget",
                children=map_style_content
            )
        ]
    )
    
    return panel
