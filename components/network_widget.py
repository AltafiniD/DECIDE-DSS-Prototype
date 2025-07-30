# components/network_widget.py
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def create_network_histogram_figure(metric_series, metric_name, n_bins=30):
    """
    Creates an interactive histogram for the distribution of a network metric.
    Each bar contains customdata with its specific [start, end] range.
    """
    if metric_series is None or metric_series.empty or metric_name is None:
        # Create a blank figure with a message if there's no data
        fig = go.Figure()
        fig.update_layout(
            title="No data to display",
            xaxis={'visible': False},
            yaxis={'visible': False},
            annotations=[{
                'text': 'No network data to display for this filter.',
                'xref': 'paper', 'yref': 'paper',
                'showarrow': False, 'font': {'size': 14}
            }]
        )
    else:
        # Use numpy to get histogram bin counts and edges, which is more reliable
        counts, bin_edges = np.histogram(metric_series, bins=n_bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        # Create customdata for each bar. This is a list of lists, where each inner
        # list is the [start, end] range for that specific bar.
        custom_data = [[bin_edges[i], bin_edges[i+1]] for i in range(len(counts))]

        # Create the figure using Plotly Graph Objects for more control
        fig = go.Figure(go.Bar(
            x=bin_centers,
            y=counts,
            customdata=custom_data,
            # The hovertemplate uses the customdata to show the precise range
            hovertemplate='<b>Range</b>: %{customdata[0]:.2f} - %{customdata[1]:.2f}<br><b>Count</b>: %{y}<extra></extra>'
        ))

        fig.update_layout(
            title=f"Distribution of {metric_name}",
            yaxis_title="Number of Road Segments",
            xaxis_title=metric_name,
            showlegend=False,
            bargap=0.1,
            # Enable click events on the figure
            clickmode='event'
        )

    # Apply consistent styling for all figures
    fig.update_layout(
        margin=dict(l=40, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black")
    )
    return fig
