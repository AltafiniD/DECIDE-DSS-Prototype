# components/deprivation_widget.py
import plotly.graph_objects as go
import pandas as pd
import math

def create_deprivation_bar_chart(deprivation_df, title=""):
    """
    Creates a horizontal bar chart summing household observations by deprivation percentile.
    """
    if deprivation_df.empty or 'Percentile' not in deprivation_df.columns or 'Observation' not in deprivation_df.columns:
        fig = go.Figure()
        fig.update_layout(
            annotations=[dict(text='No Data Available', showarrow=False, font=dict(size=16))],
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis={'visible': False}, yaxis={'visible': False}
        )
        return fig

    # Ensure required columns are numeric and handle potential errors
    deprivation_df['Percentile'] = pd.to_numeric(deprivation_df['Percentile'], errors='coerce')
    deprivation_df['Observation'] = pd.to_numeric(deprivation_df['Observation'], errors='coerce')
    deprivation_df.dropna(subset=['Percentile', 'Observation'], inplace=True)

    if deprivation_df.empty:
        fig = go.Figure()
        fig.update_layout(
            annotations=[dict(text='No matching data', showarrow=False, font=dict(size=16))],
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis={'visible': False}, yaxis={'visible': False}
        )
        return fig


    # Create 10 percentile bins (0-10, 10-20, etc.)
    bins = list(range(0, 101, 10))
    labels = [f'{i}-{i+10}%' for i in range(0, 100, 10)]
    deprivation_df['percentile_bin'] = pd.cut(
        deprivation_df['Percentile'],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True
    )

    # --- MODIFIED: Added observed=True to silence the FutureWarning ---
    observation_sum = deprivation_df.groupby('percentile_bin', observed=True)['Observation'].sum().reindex(labels, fill_value=0).sort_index()

    # Define color scale similar to the map's blue gradient
    blue_scale = [
        '#eff3ff', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6',
        '#2171b5', '#08519c', '#08306b', '#08306b', '#08306b'
    ]

    fig = go.Figure(go.Bar(
        y=observation_sum.index,
        x=observation_sum.values,
        orientation='h',
        marker_color=blue_scale,
        text=[f'{v:,.0f}' for v in observation_sum.values], # Format numbers with commas
        textposition='auto',
    ))

    fig.update_layout(
        title_text=title,
        xaxis_title="Number of Households",
        yaxis_title="Deprivation Percentile",
        yaxis=dict(autorange="reversed"), # Show 0-10% at the top
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=80, r=20, t=40, b=40),
        font=dict(color="black")
    )

    return fig

