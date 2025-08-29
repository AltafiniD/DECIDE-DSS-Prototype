# components/network_widget.py
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def create_network_histogram_figure(metric_series, metric_name):
    """
    Creates a variable-width histogram based on deciles to show data density,
    with colors matching the map display.
    """
    if metric_series is None or metric_series.empty or metric_name is None:
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
        try:
            # Get the 10 decile bins and their value ranges (edges)
            deciles, bin_edges = pd.qcut(metric_series, 10, labels=False, retbins=True, duplicates='drop')
            
            counts = deciles.value_counts().sort_index()
            bar_widths = np.diff(bin_edges)
            bar_heights = counts / bar_widths
            bar_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

            # Define a less saturated color scale for the bars
            colors = []
            for i in range(10):
                norm = i / 9.0  # Normalize decile index from 0-9 to 0-1
                r = int((255 * (norm * 2) if norm > 0.5 else 0) * 0.7 + 255 * 0.3)
                g = int((255 * (1 - abs(norm - 0.5) * 2)) * 0.7 + 255 * 0.3)
                b = int((255 * (1 - norm * 2) if norm < 0.5 else 0) * 0.7 + 255 * 0.3)
                colors.append(f'rgb({r},{g},{b})')

            # --- FIXED: Use a standard list for customdata to ensure it's passed on click ---
            custom_data_list = [
                [bin_edges[i], bin_edges[i+1], counts.iloc[i]] for i in range(len(counts))
            ]

            # Create the histogram using go.Bar
            fig = go.Figure(go.Bar(
                x=bar_centers,
                y=bar_heights,
                width=bar_widths,
                marker_color=colors,
                hovertemplate=(
                    '<b>Range:</b> %{customdata[0]:.2f} - %{customdata[1]:.2f}<br>'
                    '<b>Count:</b> %{customdata[2]}<br>'
                    '<b>Density:</b> %{y:.2f}<extra></extra>'
                ),
                customdata=custom_data_list # Use the standard list here
            ))

            fig.update_layout(
                # title=f"Density Distribution of {metric_name} by Decile",
                yaxis_title="Number of Road Segments",
                xaxis_title=f"Value of {metric_name}",
                showlegend=False,
                bargap=0,
                clickmode='event' # Ensure click events are enabled
            )

        except ValueError:
            # Fallback for when deciles can't be calculated
            fig = go.Figure()
            fig.update_layout(
                title=f"Distribution of {metric_name}",
                xaxis={'visible': False}, yaxis={'visible': False},
                annotations=[{
                    'text': 'Could not split data into deciles. Too few unique values.',
                    'xref': 'paper', 'yref': 'paper',
                    'showarrow': False, 'font': {'size': 14}
                }]
            )

    # Apply consistent styling
    fig.update_layout(
        margin=dict(l=40, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black")
    )
    return fig
