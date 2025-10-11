# app.py

import dash
import sys
import os
import numpy as np
import pandas as pd
from pydeck.bindings import json_tools

from layouts.main_layout import create_layout
from callbacks.map_callbacks import register_callbacks as register_map_callbacks
from callbacks.ui_callbacks import register_callbacks as register_ui_callbacks
from callbacks.widget_callbacks import register_callbacks as register_widget_callbacks
from callbacks.filter_callbacks import register_callbacks as register_filter_callbacks
from callbacks.chat_callbacks import register_callbacks as register_chat_callbacks
from callbacks.settings_callbacks import register_callbacks as register_settings_callbacks
from callbacks import widget_callbacks

_original_default = json_tools.default_serialize

# handle errors with parquet files
# converter
def _custom_serializer(o):
    """A robust serializer that handles all common numpy and pandas types."""
    if isinstance(o, (np.integer, np.int64)):
        return int(o)
    if isinstance(o, (np.floating, np.float64)):
        # Important: Check for NaN before converting, as float(np.nan) is still NaN
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, pd.Timestamp):
        return o.isoformat()
    # Handle pandas' special null type
    if pd.isna(o) or o is None:
        return None
    # If it's none of the special types, fall back to the original converter.
    try:
        return _original_default(o)
    except TypeError:
        return str(o) # As a last resort, convert to string

json_tools.default_serialize = _custom_serializer

sys.path.append('.')

# --- Create a temporary directory for uploads ---
os.makedirs('temp', exist_ok=True)

# --- Dash App Initialization ---
app = dash.Dash(__name__, assets_folder='assets', title='DECIDE Decision Support System v1', suppress_callback_exceptions=True)
server = app.server

# --- Custom Loading Screen with DECIDE Logo ---
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            #decide-loading-screen {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                z-index: 10000;
                transition: opacity 3.5s ease-out;
            }
            #decide-loading-screen.fade-out {
                opacity: 0;
            }
            #decide-loading-screen img {
                max-width: 500px;
                width: 80%;
                margin-bottom: 40px;
                opacity: 0.85;
                animation: fadeInScale 2s ease-out;
            }
            #decide-loading-screen .loading-spinner {
                width: 50px;
                height: 50px;
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-top-color: white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            #decide-loading-screen .loading-text {
                color: white;
                font-size: 18px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
                font-weight: 500;
                margin-top: 20px;
                animation: pulse 1.5s ease-in-out infinite;
            }
            @keyframes fadeInScale {
                0% { opacity: 0; transform: scale(0.9); }
                100% { opacity: 0.85; transform: scale(1); }
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.6; }
            }
        </style>
    </head>
    <body>
        <div id="decide-loading-screen">
            <img id="decide-logo" src="/assets/DECIDE.png" alt="DECIDE Logo">
            <div class="loading-spinner"></div>
            <div class="loading-text">Initializing Decision Support System...</div>
        </div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
            // Debug image loading
            const logo = document.getElementById('decide-logo');
            logo.addEventListener('error', function() {
                console.error('Failed to load DECIDE logo from:', logo.src);
                console.log('Trying alternative paths...');
                // Try alternative paths
                const alternatives = [
                    'assets/DECIDE.png',
                    './assets/DECIDE.png',
                    '/assets/decide.png',
                    'assets/decide.png'
                ];
                let attemptIndex = 0;
                const tryNext = () => {
                    if (attemptIndex < alternatives.length) {
                        logo.src = alternatives[attemptIndex];
                        console.log('Trying:', alternatives[attemptIndex]);
                        attemptIndex++;
                    }
                };
                logo.addEventListener('error', tryNext);
                tryNext();
            });
            logo.addEventListener('load', function() {
                console.log('DECIDE logo loaded successfully from:', logo.src);
            });
            
            // Remove loading screen when app is ready
            window.addEventListener('load', function() {
                // Wait longer to ensure DSS is fully loaded
                setTimeout(function() {
                    const loadingScreen = document.getElementById('decide-loading-screen');
                    if (loadingScreen) {
                        loadingScreen.classList.add('fade-out');
                        setTimeout(() => loadingScreen.remove(), 2500);
                    }
                }, 2000);
            });
        </script>
    </body>
</html>
'''

# --- Create Layout and Register Callbacks ---
app.layout, all_pydeck_layers, dataframes = create_layout()

# Callbacks are registered AFTER the layout is fully defined.
register_map_callbacks(app, all_pydeck_layers, dataframes)
register_ui_callbacks(app)
widget_callbacks.register_callbacks(
    app,
    dataframes['crime_points'],
    dataframes['neighbourhoods'],
    dataframes['network'],
    dataframes['buildings'],
    dataframes['land_use'],
    dataframes['deprivation'],
    dataframes['population'],
    dataframes['stop_and_search']
)
register_filter_callbacks(app, dataframes['network'])
register_chat_callbacks(app)
register_settings_callbacks(app)

# --- Run the Server ---
if __name__ == "__main__":
    app.run(debug=True)
