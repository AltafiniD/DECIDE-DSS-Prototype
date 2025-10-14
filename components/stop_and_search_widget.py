# components/stop_and_search_widget.py
import plotly.express as px
import pandas as pd
from config import STOP_AND_SEARCH_COLOR_MAP # Import the map from config

# The local color map definition has been removed.

def create_stop_and_search_histogram_figure(df, title=""):
    """
    Creates a stacked bar chart of stop and search events per month,
    broken down by the object of the search, with distinct colors for each category.
    """
    if df.empty or 'Object of search' not in df.columns:
        fig = px.bar(title="No Stop & Search data for this selection")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig
    
    # Handle null values in 'Object of search' by setting them to 'None'
    df['Object of search'] = df['Object of search'].fillna('None')

    # Ensure 'Month' column exists from the datetime
    df['Month_dt'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Month_dt'].dt.to_period('M').astype(str)

    # Group by both month and object of search to create stacks
    monthly_events = df.groupby(['Month', 'Object of search']).size().reset_index(name='count')
    monthly_events = monthly_events.sort_values('Month')

    # Get unique search objects and create a complete color map
    unique_objects = monthly_events['Object of search'].unique()
    
    # Build color map, using default colors for any categories not in our predefined map
    color_map = {}
    default_colors = px.colors.qualitative.Plotly  # Plotly's default color sequence
    
    for idx, obj in enumerate(unique_objects):
        # Use the imported map
        if obj in STOP_AND_SEARCH_COLOR_MAP:
            color_map[obj] = STOP_AND_SEARCH_COLOR_MAP[obj]
        else:
            # Use default color sequence for unknown categories
            color_map[obj] = default_colors[idx % len(default_colors)]

    fig = px.bar(
        monthly_events,
        x='Month',
        y='count',
        color='Object of search',
        title=title,
        labels={'count': 'Number of Events'},
        color_discrete_map=color_map,
        custom_data=['Object of search']
    )

    fig.update_layout(
        margin=dict(l=40, r=20, t=20, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        showlegend=False,
        clickmode='event+select',
        xaxis_tickangle=-45,
        height=None,
        autosize=True
    )
    
    return fig