# callbacks/filter_callbacks.py

from dash.dependencies import Input, Output
import pandas as pd

def register_callbacks(app, network_df):
    """
    Registers callbacks that manage the filter controls themselves.
    """
    @app.callback(
        Output('network-range-slider', 'min'),
        Output('network-range-slider', 'max'),
        Output('network-range-slider', 'value'),
        Output('network-range-slider', 'marks'),
        Input('network-metric-dropdown', 'value')
    )
    def update_network_slider(selected_metric):
        """
        Updates the network range slider's properties based on the selected metric.
        """
        if not selected_metric or selected_metric not in network_df.columns:
            return 0, 1, [0, 1], {}
        
        # Ensure the column is numeric, coercing errors
        metric_series = pd.to_numeric(network_df[selected_metric], errors='coerce').dropna()
        
        if metric_series.empty:
            return 0, 1, [0, 1], {}

        min_val = metric_series.min()
        max_val = metric_series.max()

        # Create marks for the slider
        marks = {
            min_val: f'{min_val:,.2f}',
            max_val: f'{max_val:,.2f}'
        }

        return min_val, max_val, [min_val, max_val], marks

