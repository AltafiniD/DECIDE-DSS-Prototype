# callbacks/filter_callbacks.py

from dash.dependencies import Input, Output
import pandas as pd
from utils.cache import get_dataframe # Use the new cache

# The network_df is no longer passed in here.
def register_callbacks(app):
    """
    Registers callbacks that manage the filter controls themselves.
    Data is now fetched from the cache within the callback.
    """
    @app.callback(
        Output('network-range-slider', 'min'),
        Output('network-range-slider', 'max'),
        Output('network-range-slider', 'value', allow_duplicate=True),
        Output('network-range-slider', 'marks'),
        Input('network-metric-dropdown', 'value'),
        prevent_initial_call=True
    )
    def update_network_slider(selected_metric):
        """
        Updates the network range slider's properties based on the selected metric.
        """
        # THE FIX: Fetch the network dataframe from the cache only when this callback runs.
        network_df = get_dataframe('network')
        
        if not selected_metric or selected_metric not in network_df.columns:
            return 0, 1, [0, 1], {}
        
        metric_series = pd.to_numeric(network_df[selected_metric], errors='coerce').dropna()
        
        if metric_series.empty:
            return 0, 1, [0, 1], {}

        min_val = metric_series.min()
        max_val = metric_series.max()

        # Round marks to avoid float precision issues in the UI
        marks = {
            round(min_val, 2): f'{min_val:,.2f}',
            round(max_val, 2): f'{max_val:,.2f}'
        }

        return min_val, max_val, [min_val, max_val], marks
