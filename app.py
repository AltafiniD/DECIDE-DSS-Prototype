# app.py

import dash
import sys
# --- NEW: Add project root to the Python path ---
sys.path.append('.')

from layouts.main_layout import create_layout
from callbacks.map_callbacks import register_callbacks as register_map_callbacks
from callbacks.ui_callbacks import register_callbacks as register_ui_callbacks
from callbacks.widget_callbacks import register_callbacks as register_widget_callbacks
from callbacks.filter_callbacks import register_callbacks as register_filter_callbacks
# --- MODIFIED: Updated import path ---
from callbacks.chat_callbacks import register_callbacks as register_chat_callbacks
from callbacks import widget_callbacks

# --- Dash App Initialization ---
app = dash.Dash(__name__, assets_folder='assets')
server = app.server

# --- Create Layout and Register Callbacks ---
app.layout, all_pydeck_layers, dataframes = create_layout()

# Register the different sets of callbacks
register_map_callbacks(app, all_pydeck_layers, dataframes)
register_ui_callbacks(app)
widget_callbacks.register_callbacks(app, dataframes['crime_points'], dataframes['neighbourhoods'], dataframes['network'])
register_filter_callbacks(app, dataframes['network'])
register_chat_callbacks(app)

# --- Run the Server ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
