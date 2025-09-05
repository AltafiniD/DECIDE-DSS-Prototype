# components/jenks_histogram_widget.py
import plotly.graph_objects as go
import pandas as pd
import jenkspy

def create_jenks_histogram_figure(data_series, metric_name, num_breaks=3):
    """
    Creates a histogram with variable-width bins based on Jenks natural breaks.
    """
    if data_series is None or data_series.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available for this metric.")
        return fig

    unique_values_count = data_series.nunique()
    if unique_values_count < 2:
        fig = go.Figure()
        fig.update_layout(
            annotations=[dict(
                text="Not enough unique data points to create breaks.",
                showarrow=False, font=dict(size=14)
            )]
        )
        return fig

    actual_num_breaks = min(num_breaks, unique_values_count)

    # Calculate Jenks breaks
    breaks = jenkspy.jenks_breaks(data_series, n_classes=actual_num_breaks)
    
    # --- FIX: Ensure break points are unique before creating labels ---
    unique_breaks = sorted(list(set(breaks)))
    
    # Create labels based on the unique breaks
    labels = []
    for i in range(len(unique_breaks) - 1):
        if unique_breaks[i] == unique_breaks[i+1]:
             labels.append(f"{unique_breaks[i]:.2f}")
        else:
            labels.append(f"{unique_breaks[i]:.2f} - {unique_breaks[i+1]:.2f}")
    
    # Bin the data using the unique breaks and the new labels
    binned_data = pd.cut(data_series, bins=unique_breaks, labels=labels, include_lowest=True)
    
    counts = binned_data.value_counts().sort_index()

    # Define a color scale (e.g., blues)
    colors = ['#eff3ff', '#bdd7e7', '#6baed6', '#3182bd', '#08519c']

    fig = go.Figure(go.Bar(
        x=counts.index,
        y=counts.values,
        text=counts.values,
        textposition='auto',
        marker_color=colors[:len(counts)]
    ))

    fig.update_layout(
        xaxis_title=f"Value of {metric_name}",
        yaxis_title="Number of Segments",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=40, b=20),
        font=dict(color="black")
    )
    return fig

