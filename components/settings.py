# components/settings.py
from dash import dcc, html
from config import LAYER_CONFIG, FLOOD_LAYER_CONFIG

def create_settings_modal():
    """
    Creates the settings modal window with a two-column layout.
    This component is hidden by default and is made visible by a callback.
    """
    # --- MODIFIED: Dynamically create an upload component for each data layer ---
    upload_items = []
    # Combine both layer configs to get all possible files
    all_configs = {**LAYER_CONFIG, **FLOOD_LAYER_CONFIG}
    
    # Sort by label for consistent order
    sorted_configs = sorted(all_configs.items(), key=lambda item: item[1].get('label', item[0]))

    for layer_id, config in sorted_configs:
        # Only add an upload option if a file_path is defined
        if 'file_path' in config:
            upload_items.append(
                html.Div(
                    className="settings-upload-item",
                    children=[
                        # Use the layer's label for display
                        config.get('label', layer_id),
                        # The ID is a dictionary to identify which layer was updated
                        dcc.Upload(
                            html.Button("Upload File"),
                            id={'type': 'upload-layer', 'index': layer_id}
                        )
                    ]
                )
            )

    return html.Div(
        id="settings-modal-overlay",
        className="settings-modal-overlay-hidden",
        children=[
            html.Div(
                id="settings-modal",
                className="settings-modal",
                children=[
                    html.Div(
                        className="settings-modal-header",
                        children=[
                            html.H2("Settings"),
                            html.Button("×", id="settings-modal-close-btn", className="settings-modal-close-btn")
                        ]
                    ),
                    html.Div(
                        className="settings-modal-body",
                        children=[
                            html.Div(
                                className="settings-column",
                                children=[
                                    html.H4("Display Options"),
                                    html.Div(className="settings-toggle-item", children=[
                                        "Show tooltips on hover",
                                        html.Button("On", className="toggle-switch")
                                    ]),
                                    html.Div(className="settings-toggle-item", children=[
                                        "Animate layer transitions",
                                        html.Button("On", className="toggle-switch")
                                    ]),
                                    # --- NEW: A div to show upload status messages ---
                                    html.Div(id='upload-status-notification', style={'marginTop': '20px'})
                                ]
                            ),
                            html.Div(
                                className="settings-column",
                                children=[
                                    html.H4("Upload Custom Data"),
                                    html.P("Replace default layers with your own GeoJSON files.",
                                           style={'fontSize': '14px', 'color': '#666'}),
                                    *upload_items,  # Unpack the dynamically generated list
                                    html.P("To remove custom uploads, navigate to <dss_folder>/temp and remove the uploaded file.",
                                           style={'fontSize': '14px', 'color': '#666', 'marginTop': '10px'})
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

