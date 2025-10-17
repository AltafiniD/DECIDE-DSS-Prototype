# components/network_widget.py
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from config import FLOOD_HAZARD_COLORS 

# --- NEW UTILITY FUNCTION: Generates a color gradient ---
def get_color_gradient(base_rgb, steps, output_hex=True, light_mix=0.1):
    """
    Generates a color gradient from a lighter mix (white) to the base_rgb (darker).
    
    - light_mix: The starting point of the gradient (e.g., 0.1 for 10% mix of base color).
    - output_hex: True for Plotly (histograms), False for Pydeck (map).
    """
    start_rgb = np.array([255, 255, 255])
    end_rgb = np.array(base_rgb)
    
    # Interpolation steps: Start with 'light_mix' of the base color up to 100%
    t_adjusted = np.linspace(light_mix, 1, steps, endpoint=True) 
    
    # Linear interpolation (Mix = (1-t)*White + t*BaseColor)
    gradient_rgb = [(1 - i) * start_rgb + i * end_rgb for i in t_adjusted]
    
    # Clamp values and convert to int
    gradient_rgb = [np.clip(rgb.astype(int), 0, 255) for rgb in gradient_rgb]

    if output_hex:
        def rgb_to_hex(rgb):
            return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        return [rgb_to_hex(rgb) for rgb in gradient_rgb]
    else:
        return [tuple(rgb) for rgb in gradient_rgb]
# --------------------------------------------------------


def create_network_histogram_figure(metric_series, metric_name):
    """
    Creates a histogram with 100 bins, colored by 10 decile breaks,
    to show data density. Clicking a bin filters by its decile.
    Color scale changes based on the metric name.
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
        return fig
    else:
        try:
            # 1. Calculate the 10 decile breaks for coloring and filtering
            _, decile_edges = pd.qcut(metric_series, 10, labels=False, retbins=True, duplicates='drop')
            num_deciles = len(decile_edges) - 1

            # 2. Create 100 bins for the visual representation
            num_fine_bins = 100
            counts, bin_edges_fine = np.histogram(metric_series, bins=num_fine_bins)
            bar_centers = (bin_edges_fine[:-1] + bin_edges_fine[1:]) / 2
            bar_widths = np.diff(bin_edges_fine)
            
            # --- NEW COLOR LOGIC START ---
            base_color = None
            if '_rivers_risk' in metric_name:
                base_color = FLOOD_HAZARD_COLORS['rivers_risk']['high'][:3]
            elif '_sea_risk' in metric_name:
                base_color = FLOOD_HAZARD_COLORS['sea_risk']['high'][:3]
            elif '_surface_risk' in metric_name:
                base_color = FLOOD_HAZARD_COLORS['surface_risk']['high'][:3]
            
            if base_color and num_deciles > 1:
                # Flood Metrics: Generate the N-step HEX gradient (Lightest to Darkest)
                color_gradient = get_color_gradient(base_color, steps=num_deciles, output_hex=True)
            else:
                # Other Network Metrics (NACH, NAIN, NADC): Custom Rainbow scale (Blue=Low, Red=High)
                default_scale = [
                    "#0000d3",  # 0: Dark Blue (Low)
                    "#003cff",  # 1: Blue
                    "#008cff",  # 2: Light Blue
                    '#00ccff',  # 3: Cyan
                    "#00ebbc",  # 4: Light Cyan/Green
                    "#00c40a",  # 5: Green
                    "#ffd900",  # 6: Yellow
                    '#ffaa00',  # 7: Orange
                    '#ff5500',  # 8: Red-Orange
                    '#cc0000'   # 9: Dark Red (High)
                ] 
                color_gradient = default_scale[:num_deciles]
                if num_deciles > len(default_scale):
                     color_gradient.extend([default_scale[-1]] * (num_deciles - len(default_scale)))
            
            # --- NEW COLOR LOGIC END ---

            # Use the decile edges to assign the correct color from the gradient
            bar_colors = []
            
            for bin_center in bar_centers:
                # np.digitize returns the index of the class/decile (0 to num_deciles-1)
                decile_index = np.digitize(bin_center, decile_edges[1:-1]) 
                decile_index = np.clip(decile_index, 0, num_deciles - 1) 
                bar_colors.append(color_gradient[decile_index]) 
                
            # Prepare custom data for hover template
            custom_data_list = []
            for center in bar_centers:
                decile_index = np.digitize(center, decile_edges[1:-1])
                decile_index = np.clip(decile_index, 0, num_deciles - 1)
                lower = decile_edges[decile_index]
                upper = decile_edges[decile_index + 1]
                custom_data_list.append([lower, upper])

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
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#000000", family='Arial'),
        xaxis={'layer': 'above traces'},
        yaxis={'layer': 'above traces'}
        # ----------------------
    )
    return fig