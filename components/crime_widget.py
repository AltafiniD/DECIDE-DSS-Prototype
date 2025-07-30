# components/crime_widget.py
import plotly.express as px
import pandas as pd

# The parameter name remains 'colour_map' to respect the user's preference.
def create_crime_histogram_figure(crime_df, colour_map, title="Crimes per Month by Type"):
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
            # THE FIX: Reverted to the correct Plotly keyword argument 'color'.
            color='Crime type',
            title=title,
            labels={'count': 'Number of Crimes'},
            # THE FIX: Reverted to the correct Plotly keyword argument 'color_discrete_map'.
            color_discrete_map=colour_map,
            custom_data=['Crime type']
        )
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"), # This is a library property, must remain 'color'
        showlegend=False,
        clickmode='event+select'
    )
    return fig
