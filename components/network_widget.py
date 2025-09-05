# components/network_widget.py
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def create_network_histogram_figure(metric_series, metric_name):
    """
    Creates a histogram with 100 bins, colored by 10 decile breaks,
    to show data density. Clicking a bin filters by its decile.
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
            # 1. Calculate the 10 decile breaks for coloring and filtering
            _, decile_edges = pd.qcut(metric_series, 10, labels=False, retbins=True, duplicates='drop')

            # 2. Create 100 bins for the visual representation
            num_fine_bins = 100
            counts, bin_edges_fine = np.histogram(metric_series, bins=num_fine_bins)

            bar_centers = (bin_edges_fine[:-1] + bin_edges_fine[1:]) / 2
            bar_widths = np.diff(bin_edges_fine)

            # 3. Assign a color and customdata to each of the 100 bins based on its decile
            bar_colors = []
            custom_data_list = []
            
            # Define the rainbow color scale for the 10 deciles
            decile_colors = []
            for i in range(10):
                norm = i / 9.0
                r = int(255 * (norm * 2)) if norm > 0.5 else 0
                g = int(255 * (1 - abs(norm - 0.5) * 2))
                b = int(255 * (1 - norm * 2)) if norm < 0.5 else 0
                decile_colors.append(f'rgb({r},{g},{b})')

            for center in bar_centers:
                # Find which decile the center of the bar falls into
                decile_index = -1
                for i in range(len(decile_edges) - 1):
                    # Handle the last bin edge inclusively
                    is_last_edge = (i == len(decile_edges) - 2)
                    if (decile_edges[i] <= center <= decile_edges[i+1]) or \
                       (is_last_edge and center == decile_edges[i+1]):
                        decile_index = i
                        break
                
                if decile_index != -1:
                    bar_colors.append(decile_colors[decile_index])
                    # The customdata stores the range of the DECİLE, not the fine bin
                    custom_data_list.append([decile_edges[decile_index], decile_edges[decile_index+1]])
                else:
                    # Fallback for any points that might fall outside
                    bar_colors.append('rgb(200,200,200)')
                    custom_data_list.append([metric_series.min(), metric_series.max()])

            # 4. Create the figure with go.Bar
            fig = go.Figure(go.Bar(
                x=bar_centers,
                y=counts,
                width=bar_widths,
                marker_color=bar_colors,
                hovertemplate=(
                    '<b>Decile Range:</b> %{customdata[0]:.2f} - %{customdata[1]:.2f}<br>'
                    '<b>Bin Count:</b> %{y}<extra></extra>'
                ),
                customdata=custom_data_list
            ))

            fig.update_layout(
                yaxis_title="Number of Road Segments",
                xaxis_title=f"Value of {metric_name}",
                showlegend=False,
                bargap=0,
                clickmode='event'
            )

        except (ValueError, IndexError):
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
