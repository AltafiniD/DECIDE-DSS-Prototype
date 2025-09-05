# components/population_widget.py
import plotly.graph_objects as go
import pandas as pd
import jenkspy

def create_population_density_histogram(population_df, num_breaks=5):
    """
    Creates a histogram for population density using Jenks natural breaks.
    """
    # Ensure the 'density' column exists and is numeric
    if population_df is None or population_df.empty or 'density' not in population_df.columns:
        fig = go.Figure()
        fig.update_layout(title="No population data available.")
        return fig

    data_series = pd.to_numeric(population_df['density'], errors='coerce').dropna()
    
    if data_series.empty:
        fig = go.Figure()
        fig.update_layout(title="No density data to display.")
        return fig

    unique_values_count = data_series.nunique()
    if unique_values_count < 2:
        fig = go.Figure()
        fig.update_layout(annotations=[dict(text="Not enough unique data to create breaks.", showarrow=False)])
        return fig

    # Calculate Jenks breaks
    actual_num_breaks = min(num_breaks, unique_values_count)
    breaks = jenkspy.jenks_breaks(data_series, n_classes=actual_num_breaks)
    unique_breaks = sorted(list(set(breaks)))
    
    # Create labels for the bins
    labels = [f"{unique_breaks[i]:.2f} - {unique_breaks[i+1]:.2f}" for i in range(len(unique_breaks) - 1)]
    
    binned_data = pd.cut(data_series, bins=unique_breaks, labels=labels, include_lowest=True)
    counts = binned_data.value_counts().sort_index()

    # Use a color scale (e.g., purples/magentas to match the map layer)
    colors = ['#fde0dd', '#fa9fb5', '#f768a1', '#c51b8a', '#7a0177']

    fig = go.Figure(go.Bar(
        x=counts.index,
        y=counts.values,
        text=counts.values,
        textposition='auto',
        marker_color=colors[:len(counts)]
    ))

    fig.update_layout(
        xaxis_title="Population Density",
        yaxis_title="Number of Areas",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=40, b=20),
        font=dict(color="black")
    )
    return fig
