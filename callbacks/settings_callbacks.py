# callbacks/settings_callbacks.py

import base64
import os
from dash.dependencies import Input, Output, State, ALL
from dash import html, no_update, ctx
import json

from config import LAYER_CONFIG, FLOOD_LAYER_CONFIG

def register_callbacks(app):
    """
    Registers all settings-related callbacks, including file uploads.
    """
    @app.callback(
        Output('url', 'href'),
        Output('upload-status-notification', 'children'),
        Input({'type': 'upload-layer', 'index': ALL}, 'contents'),
        State({'type': 'upload-layer', 'index': ALL}, 'filename'),
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def handle_file_uploads(list_of_contents, list_of_filenames, pathname):
        """
        This callback saves an uploaded GeoJSON to a temporary folder and reloads the page.
        It does NOT overwrite the original data files.
        """
        print("\n--- File Upload Callback Triggered ---")

        if not ctx.triggered_id:
            print("Callback triggered with no specific input. Aborting.")
            return no_update, no_update

        triggered_id = ctx.triggered_id
        layer_id = triggered_id['index']
        print(f"Triggered by component: {triggered_id}")

        content = None
        filename = None
        for i, input_spec in enumerate(ctx.inputs_list[0]):
            if input_spec['id'] == triggered_id:
                content = list_of_contents[i]
                filename = list_of_filenames[i]
                break
        
        if not content:
            print("No file content found. Aborting.")
            return no_update, no_update

        print(f"File '{filename}' selected for layer '{layer_id}'.")

        all_configs = {**LAYER_CONFIG, **FLOOD_LAYER_CONFIG}
        original_path = all_configs.get(layer_id, {}).get('file_path')

        if not original_path:
            error_message = f"❌ Error: No file path is configured for layer '{layer_id}'."
            print(f"Configuration error: {error_message}")
            return no_update, html.Div(error_message, style={'color': 'red', 'marginTop': '10px'})

        temp_dir = 'temp'
        target_path = os.path.join(temp_dir, os.path.basename(original_path))
        print(f"Target path for temporary file: '{target_path}'")
        
        try:
            print("Decoding file content...")
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)

            print(f"Writing {len(decoded)} bytes to '{target_path}'...")
            with open(target_path, 'wb') as f:
                f.write(decoded)
            print("File write successful.")

            # --- NEW: Trigger Dash's hot-reloader by "touching" the main app file ---
            print("Touching app.py to trigger server reload...")
            os.utime('app.py', None)

            message = f"✅ Success! Using '{filename}' for this session. Server is restarting..."
            # The browser reload via href is a good fallback, but the hot-reload should handle it.
            return pathname, html.Div(message, style={'color': 'green', 'marginTop': '10px'})

        except Exception as e:
            error_message = f"❌ Error processing '{filename}': {e}"
            print(f"An exception occurred: {e}")
            return no_update, html.Div(error_message, style={'color': 'red', 'marginTop': '10px'})

