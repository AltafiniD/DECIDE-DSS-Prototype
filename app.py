# app.py

import dash
import sys
sys.path.append('.')

from layouts.main_layout import create_layout
from callbacks.map_callbacks import register_callbacks as register_map_callbacks
from callbacks.ui_callbacks import register_callbacks as register_ui_callbacks
from callbacks.widget_callbacks import register_callbacks as register_widget_callbacks
from callbacks.filter_callbacks import register_callbacks as register_filter_callbacks
from callbacks.chat_callbacks import register_callbacks as register_chat_callbacks
from callbacks import widget_callbacks

# --- Dash App Initialization ---
app = dash.Dash(__name__, assets_folder='assets')
server = app.server

# --- Create Layout and Register Callbacks ---
# This line is critical. It calls create_layout() which builds ALL components
# (including the settings modal) and assigns the entire structure to app.layout.
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
    dataframes['deprivation']
)
register_filter_callbacks(app, dataframes['network'])
register_chat_callbacks(app)

# --- Run the Server ---
if __name__ == "__main__":
    app.run(debug=True)
