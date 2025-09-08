# components/stop_and_search_widget.py
import plotly.express as px
import pandas as pd

def create_stop_and_search_histogram_figure(df, title=""):
    """
    Creates a stacked bar chart of stop and search events per month,
    broken down by the object of the search, with all bars in a single color.
    """
    if df.empty or 'Object of search' not in df.columns:
        fig = px.bar(title="No Stop & Search data for this selection")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Ensure 'Month' column exists from the datetime
    df['Month_dt'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Month_dt'].dt.to_period('M').astype(str)

    # --- MODIFIED: Group by both month and object of search to create stacks ---
    monthly_events = df.groupby(['Month', 'Object of search']).size().reset_index(name='count')
    monthly_events = monthly_events.sort_values('Month')

    # --- NEW: Create a color map that forces all categories to be the same color ---
    search_types = monthly_events['Object of search'].unique()
    single_color = 'rgb(220, 20, 60)'
    color_map = {stype: single_color for stype in search_types}

    fig = px.bar(
        monthly_events,
        x='Month',
        y='count',
        # --- MODIFIED: Color by object of search to create the stacks ---
        color='Object of search',
        title=title,
        labels={'count': 'Number of Events'},
        # --- NEW: Use the color map to make all stacks the same color ---
        color_discrete_map=color_map,
        # --- NEW: Add custom_data to ensure 'Object of search' is available on click ---
        custom_data=['Object of search']
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        # --- Keep the legend hidden as requested ---
        showlegend=False,
        # --- NEW: Make the bars clickable ---
        clickmode='event+select'
    )
    return fig
