# components/flood_risk_widget.py
import plotly.graph_objects as go
import pandas as pd
from config import BUILDING_COLOR_CONFIG

def create_flood_risk_pie_chart(df, hazard_column, title="Flood Hazard Distribution"):
    """
    Creates a pie chart for flood hazard distribution of buildings.

    Args:
        df (pd.DataFrame): The dataframe containing building data.
        hazard_column (str): The column name for the specific flood hazard
                           (e.g., 'sea_hazard').
        title (str): The title for the chart.

    Returns:
        go.Figure: A Plotly graph object figure.
    """
    if df.empty or hazard_column not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            title="No building data for this selection",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Handle null values as 'Not at hazard'
    hazard_data = df[hazard_column].fillna('Not at hazard')
    hazard_counts = hazard_data.value_counts()
    
    # --- MODIFIED: Map new hazard column names to the existing config keys ---
    hazard_key_map = {
        'surface_hazard': 'risk_watercourses',
        'river_hazard': 'risk_rivers',
        'sea_hazard': 'risk_sea'
    }
    config_key = hazard_key_map.get(hazard_column)
    color_map = {}
    if config_key and config_key in BUILDING_COLOR_CONFIG:
        color_map = {
            level.capitalize(): f'rgb({",".join(map(str, rgba[:3]))})'
            for level, rgba in BUILDING_COLOR_CONFIG[config_key]['colors'].items()
        }
    
    # Add a specific color for the 'Not at hazard' category
    color_map['Not at hazard'] = 'rgb(200, 200, 200)'

    if hazard_counts.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"No '{hazard_column.replace('_', ' ')}' data",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Capitalize labels for consistent matching with the color map
    fig = go.Figure(data=[go.Pie(
        labels=hazard_counts.index.str.capitalize(),
        values=hazard_counts.values,
        hole=.3,
        marker_colors=[color_map.get(label.capitalize(), 'lightgrey') for label in hazard_counts.index],
        textinfo='percent+label'
    )])

    fig.update_layout(
        title_text=title,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        showlegend=False
    )
    return fig
