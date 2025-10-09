# components/population_widget.py
import plotly.graph_objects as go
import pandas as pd
import jenkspy
# ADDED: Import html and dcc for combining widgets
from dash import html, dcc 

def create_population_density_histogram(population_df, num_breaks=5):
    """
    Creates a histogram for population density using 10 Jenks natural breaks.
    FIXED: Now uses 10 bins with proper color gradient.
    """
    if population_df is None or population_df.empty or 'density' not in population_df.columns:
        fig = go.Figure()
        fig.update_layout(
            title="No population data available.",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300
        )
        return fig

    data_series = pd.to_numeric(population_df['density'], errors='coerce').dropna()
    
    if data_series.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No density data to display.",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300
        )
        return fig

    unique_values_count = data_series.nunique()
    if unique_values_count < 2:
        fig = go.Figure()
        fig.update_layout(
            annotations=[dict(text="Not enough unique data to create breaks.", showarrow=False)],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300
        )
        return fig

    # FIXED: Use 10 breaks
    actual_num_breaks = min(10, unique_values_count)
    breaks = jenkspy.jenks_breaks(data_series, n_classes=actual_num_breaks)
    unique_breaks = sorted(list(set(breaks)))
    
    # Create labels for the bins
    labels = [f"{unique_breaks[i]:.1f}-{unique_breaks[i+1]:.1f}" for i in range(len(unique_breaks) - 1)]
    
    binned_data = pd.cut(data_series, bins=unique_breaks, labels=labels, include_lowest=True)
    counts = binned_data.value_counts().sort_index()

    # FIXED: 10-color gradient from light to dark purple/magenta
    colors = [
    '#0d2258',   # Darkest (Dark Blue/Purple)
    '#0e6b8c',
    '#2197b0',
    '#40beaf',
    '#65d496',
    '#8be67d',
    '#aef258',
    '#cbf738',
    '#e1f725',
    '#f0f921'    # Lightest (Yellow)
]
    
    # Use only as many colors as we have bins
    colors_to_use = colors[:len(counts)]

    fig = go.Figure(go.Bar(
        x=counts.index,
        y=counts.values,
        text=counts.values,
        textposition='auto',
        marker_color=colors_to_use,
        hovertemplate='%{x}<br>Count: %{y}<extra></extra>'
    ))

    fig.update_layout(
        xaxis_title="Population Density",
        yaxis_title="Number of Areas",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=40, b=80),
        font=dict(color="black"),
        height=300,
        xaxis=dict(tickangle=-45)
    )
    return fig

def create_total_population_widget(population_df):
    """
    Creates an Indicator widget for total population from the 'all_residents' column.
    """
    fig = go.Figure()

    if population_df is None or population_df.empty or 'all_residents' not in population_df.columns:
        fig.add_annotation(
            text="No population data", 
            showarrow=False, 
            x=0.5, y=0.5, 
            xref="paper", yref="paper"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            margin=dict(l=0, r=0, t=10, b=10),
            height=50
        )
        return fig

    series = pd.to_numeric(population_df['all_residents'], errors='coerce').dropna()
    if series.empty:
        fig.add_annotation(
            text="No valid population values", 
            showarrow=False, 
            x=0.5, y=0.5, 
            xref="paper", yref="paper"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            margin=dict(l=0, r=0, t=10, b=10),
            height=50
        )
        return fig

    total = int(series.sum())

    fig = go.Figure(go.Indicator(
        mode="number",
        value=total,
        number={"valueformat": ",", "font": {"size": 48, "color": "#000000"}},
        domain={"x": [0.0, 1.0], "y": [0.0, 1.0]} 
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=150
    )
    return fig

# ADDED FUNCTION to combine the two plots
def create_combined_population_widget(population_df):
    """
    Combines the Total Population and Population Density widgets into a single
    stacked component occupying full width.
    """
    total_population_fig = create_total_population_widget(population_df)
    density_histogram_fig = create_population_density_histogram(population_df)

    # Use a div with class 'widget-full-width' to ensure it spans the panel 
    # and 'widget' for the panel styling.
    return html.Div(
        className="widget widget-full-width",
        children=[
            html.Div(
                className="widget-title",
                children=dcc.Markdown("#### Population Data"),
            ),
            # Total Population (on top)
            html.Div(
                className="population-sub-widget",
                children=[
                    dcc.Markdown(
                        "Total Population",
                        style={'fontSize': '20px', 'fontWeight': '600'}
            ),
                    dcc.Graph(
                        id="total-population-widget",
                        figure=total_population_fig,
                        config={'displayModeBar': False},
                        style={'height': '50px'}
                    )
                ]
            ),
            # Population Density (below)
            html.Div(
                className="population-sub-widget",
                children=[
                         dcc.Markdown(
                        "Population Density",
                        style={'fontSize': '20px', 'fontWeight': '600'}
                         ),
                    dcc.Graph(
                        id="population-density-chart",
                        figure=density_histogram_fig,
                        config={'displayModeBar': False},
                        style={'height': '250px'}
                    )
                ]
            ),
        ]
    )
