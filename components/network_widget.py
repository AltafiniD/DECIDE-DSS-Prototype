# components/network_widget.py
import plotly.express as px
import pandas as pd
import numpy as np

def create_network_histogram_figure(network_df, title="NACH Distribution"):
    """
    Creates a histogram of the NACH values from the network data.
    """
    if network_df.empty or 'NACH' not in network_df.columns:
        return px.bar(title="No network data available")

    df = network_df.copy()
    df['NACH'] = pd.to_numeric(df['NACH'], errors='coerce')
    df.dropna(subset=['NACH'], inplace=True)

    if df.empty:
        return px.bar(title="No valid NACH data")

    # --- UPDATED: Use NumPy for robust histogram calculation to avoid pandas errors ---
    counts, bin_edges = np.histogram(df['NACH'], bins=10)
    
    # Prepare data for Plotly
    bin_labels = [f"{bin_edges[i]:.2f} to {bin_edges[i+1]:.2f}" for i in range(len(counts))]
    bin_ranges = [[bin_edges[i], bin_edges[i+1]] for i in range(len(counts))]
    
    hist_df = pd.DataFrame({
        'bin_label': bin_labels,
        'count': counts,
        'bin_edges': bin_ranges
    })

    fig = px.bar(
        hist_df,
        x='bin_label',
        y='count',
        title=title,
        labels={'bin_label': 'NACH Value Range', 'count': 'Number of Segments'},
        custom_data=['bin_edges'] # Pass the raw bin edges to the figure
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        showlegend=False,
        clickmode='event+select'
    )
    return fig
