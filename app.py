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
# --- FIXED: Corrected syntax and re-added suppress_callback_exceptions ---
app = dash.Dash(__name__, assets_folder='assets', title='Cardiff Data Explorer', suppress_callback_exceptions=True)
server = app.server

# --- Create Layout and Register Callbacks ---
app.layout, all_pydeck_layers, dataframes = create_layout()

# Callbacks are registered AFTER the layout is fully defined.
register_map_callbacks(app, all_pydeck_layers, dataframes)
register_ui_callbacks(app)
# --- MODIFIED: Pass the population and stop_and_search dataframes to the widget callbacks ---
widget_callbacks.register_callbacks(
    app,
    dataframes['crime_points'],
    dataframes['neighbourhoods'],
    dataframes['network'],
    dataframes['buildings'],
    dataframes['land_use'],
    dataframes['deprivation'],
    dataframes['population'],
    dataframes['stop_and_search'] # New dataframe added
)
register_filter_callbacks(app, dataframes['network'])
register_chat_callbacks(app)
register_settings_callbacks(app)

# --- Run the Server ---
if __name__ == "__main__":
    app.run(debug=True)
