# components/flood_risk_widget.py
import plotly.graph_objects as go
import pandas as pd
from config import BUILDING_COLOR_CONFIG

def create_flood_risk_pie_chart(df, risk_column, title="Flood Risk Distribution"):
    """
    Creates a pie chart for flood risk distribution of buildings.

    Args:
        df (pd.DataFrame): The dataframe containing building data.
        risk_column (str): The column name for the specific flood risk
                           (e.g., 'Sea_risk').
        title (str): The title for the chart.

    Returns:
        go.Figure: A Plotly graph object figure.
    """
    if df.empty or risk_column not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            title="No building data for this selection",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # --- MODIFIED: Handle null values as 'Not at risk' ---
    risk_data = df[risk_column].fillna('Not at risk')
    risk_counts = risk_data.value_counts()
    
    risk_key_map = {
        'Watercourses_Risk': 'risk_watercourses',
        'Rivers_risk': 'risk_rivers',
        'Sea_risk': 'risk_sea'
    }
    config_key = risk_key_map.get(risk_column)
    color_map = {}
    if config_key and config_key in BUILDING_COLOR_CONFIG:
        color_map = {
            level.capitalize(): f'rgb({",".join(map(str, rgba[:3]))})'
            for level, rgba in BUILDING_COLOR_CONFIG[config_key]['colors'].items()
        }
    
    # --- NEW: Add a specific color for the 'Not at risk' category ---
    color_map['Not at risk'] = 'rgb(200, 200, 200)'

    if risk_counts.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"No '{risk_column.replace('_', ' ')}' data",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # --- MODIFIED: Capitalize labels for consistent matching ---
    fig = go.Figure(data=[go.Pie(
        labels=risk_counts.index.str.capitalize(),
        values=risk_counts.values,
        hole=.3,
        marker_colors=[color_map.get(label.capitalize(), 'lightgrey') for label in risk_counts.index],
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
