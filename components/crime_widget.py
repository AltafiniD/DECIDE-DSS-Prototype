# components/crime_widget.py
import plotly.express as px
import pandas as pd
from config import CRIME_COLOR_MAP # Import the crime color map

# The 'color_map' argument has been removed from the function signature
def create_crime_histogram_figure(crime_df, title="Crimes per Month by Type"):
    """
    Creates a stacked bar chart figure of crimes per month, broken down by crime type.
    """
    if crime_df.empty:
        fig = px.bar(title="No crime data for this selection")
    else:
        # Handle null values in 'Crime type' by setting them to 'None'
        crime_df['Crime type'] = crime_df['Crime type'].fillna('None')
        
        # Ensure 'Month' column exists
        if 'Month' not in crime_df.columns:
            # Note: Assuming 'Date' column exists and is used to derive 'Month'
            crime_df['Month_dt'] = pd.to_datetime(crime_df['Date'], errors='coerce')
            crime_df['Month'] = crime_df['Month_dt'].dt.to_period('M').astype(str)

        monthly_crimes = crime_df.groupby(['Month', 'Crime type']).size().reset_index(name='count')
        monthly_crimes = monthly_crimes.sort_values('Month')
        
        # Build color map, prioritizing the imported CRIME_COLOR_MAP but allowing for defaults
        unique_crimes = monthly_crimes['Crime type'].unique()
        color_map = {}
        default_colors = px.colors.qualitative.Plotly
        
        for idx, crime_type in enumerate(unique_crimes):
            if crime_type in CRIME_COLOR_MAP:
                color_map[crime_type] = CRIME_COLOR_MAP[crime_type]
            else:
                color_map[crime_type] = default_colors[idx % len(default_colors)]
                
        fig = px.bar(
            monthly_crimes,
            x='Month',
            y='count',
            color='Crime type',
            title=title,
            labels={'count': 'Number of Crimes'},
            color_discrete_map=color_map,
            custom_data=['Crime type']
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