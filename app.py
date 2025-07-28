# app.py

import dash

from layouts.main_layout import create_layout
from callbacks.map_callbacks import register_callbacks as register_map_callbacks
from callbacks.ui_callbacks import register_callbacks as register_ui_callbacks
from callbacks.widget_callbacks import register_callbacks as register_widget_callbacks

# --- Dash App Initialization ---
app = dash.Dash(__name__, assets_folder='assets')
server = app.server

# --- Create Layout and Register Callbacks ---
app.layout, all_pydeck_layers, dataframes = create_layout()

# Register the different sets of callbacks
register_map_callbacks(app, all_pydeck_layers, dataframes)
register_ui_callbacks(app)
register_widget_callbacks(
    app,
    crime_df=dataframes['crime'],
    neighbourhoods_df=dataframes['neighbourhoods']
)

# --- Run the Server ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
