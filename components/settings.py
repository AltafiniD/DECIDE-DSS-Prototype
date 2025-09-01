# components/settings.py
from dash import dcc, html

def create_settings_modal():
    """
    Creates the settings modal window with a two-column layout.
    This component is hidden by default and is made visible by a callback.
    """
    return html.Div(
        id="settings-modal-overlay",
        className="settings-modal-overlay-hidden",  # Initially hidden
        children=[
            html.Div(
                id="settings-modal",
                className="settings-modal",
                children=[
                    # Modal Header
                    html.Div(
                        className="settings-modal-header",
                        children=[
                            html.H2("Settings"),
                            html.Button("×", id="settings-modal-close-btn", className="settings-modal-close-btn")
                        ]
                    ),
                    # Modal Body with two columns
                    html.Div(
                        className="settings-modal-body",
                        children=[
                            # Left Column for general settings (toggles)
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
                                    html.Div(className="settings-toggle-item", children=[
                                        "Enable high-contrast mode",
                                        html.Button("Off", className="toggle-switch")
                                    ]),
                                    html.Div(className="settings-toggle-item", children=[
                                        "Reduce motion",
                                        html.Button("Off", className="toggle-switch")
                                    ]),
                                ]
                            ),
                            # Right Column for data uploads
                            html.Div(
                                className="settings-column",
                                children=[
                                    html.H4("Upload Custom Data"),
                                    html.P("Replace default layers with your own GeoJSON files.",
                                           style={'fontSize': '14px', 'color': '#666'}),
                                    html.Div(className="settings-upload-item", children=[
                                        "Neighbourhoods",
                                        dcc.Upload(html.Button("Upload File"), id="upload-neighbourhoods")
                                    ]),
                                    html.Div(className="settings-upload-item", children=[
                                        "Buildings",
                                        dcc.Upload(html.Button("Upload File"), id="upload-buildings")
                                    ]),
                                    html.Div(className="settings-upload-item", children=[
                                        "Crime Data",
                                        dcc.Upload(html.Button("Upload File"), id="upload-crime")
                                    ]),
                                    html.Div(className="settings-upload-item", children=[
                                        "Road Network",
                                        dcc.Upload(html.Button("Upload File"), id="upload-network")
                                    ]),
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

