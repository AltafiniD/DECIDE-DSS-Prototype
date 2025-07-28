# components/crime_widget.py
import plotly.express as px
import pandas as pd

def create_crime_histogram_figure(crime_df, color_map, title="Crimes per Month by Type"):
    """
    Creates a stacked bar chart figure of crimes per month, broken down by crime type.
    """
    if crime_df.empty:
        fig = px.bar(title="No crime data for this selection")
    else:
        monthly_crimes = crime_df.groupby(['Month', 'Crime type']).size().reset_index(name='count')
        monthly_crimes = monthly_crimes.sort_values('Month')
        fig = px.bar(
            monthly_crimes,
            x='Month',
            y='count',
            color='Crime type',
            title=title,
            labels={'count': 'Number of Crimes'},
            color_discrete_map=color_map,
            # Add custom_data to ensure crime type is available on click
            custom_data=['Crime type']
        )
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        showlegend=False,
        # Make the bars clickable
        clickmode='event+select'
    )
    return fig
