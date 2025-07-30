# app.py

import dash

from layouts.main_layout import create_layout
from callbacks.map_callbacks import register_callbacks as register_map_callbacks
from callbacks.ui_callbacks import register_callbacks as register_ui_callbacks
from callbacks.widget_callbacks import register_callbacks as register_widget_callbacks
from callbacks.filter_callbacks import register_callbacks as register_filter_callbacks

# --- Dash App Initialization ---
app = dash.Dash(__name__, assets_folder='assets')
server = app.server

# --- Create Layout and Register Callbacks ---
app.layout, all_layers_config = create_layout()

# Register the different sets of callbacks.
register_map_callbacks(app, all_layers_config)
register_ui_callbacks(app)
register_widget_callbacks(app)
# THE FIX: No longer passing the large dataframe here.
register_filter_callbacks(app)

# --- Run the Server ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
