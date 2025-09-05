# components/sas_gender_widget.py
import plotly.graph_objects as go
import pandas as pd

def create_sas_gender_pie_chart(df):
    """
    Creates a pie chart for the gender distribution within the Stop & Search data.
    """
    if df.empty or 'Gender' not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            title="No gender data available",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Filter for only 'Male' and 'Female' and count them
    gender_counts = df[df['Gender'].isin(['Male', 'Female'])]['Gender'].value_counts()
    
    # Define colors
    colors = {'Male': '#1f77b4', 'Female': '#e377c2'}
    
    fig = go.Figure(data=[go.Pie(
        labels=gender_counts.index,
        values=gender_counts.values,
        hole=.4,
        marker_colors=[colors.get(gender, 'grey') for gender in gender_counts.index],
        textinfo='percent+label'
    )])

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        showlegend=False
    )
    
    return fig
