# components/land_use_widget.py
import plotly.express as px
import pandas as pd

def create_land_use_donut_chart(land_use_df, title=""): # title is kept for compatibility but ignored
    """
    Creates a donut chart for land use distribution, grouping small slices.
    """
    if land_use_df.empty or 'landuse_text' not in land_use_df.columns:
        fig = px.pie() # Create an empty pie
        fig.update_layout(
            annotations=[dict(text='No Data Available', showarrow=False, font=dict(size=16))],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    land_use_counts = land_use_df['landuse_text'].value_counts().reset_index()
    land_use_counts.columns = ['landuse_text', 'count']
    
    # --- NEW: Group slices smaller than 2% into an 'Other' category for clarity ---
    total_count = land_use_counts['count'].sum()
    if total_count > 0:
        land_use_counts['percentage'] = (land_use_counts['count'] / total_count) * 100
    else:
        land_use_counts['percentage'] = 0

    threshold = 2.0
    small_slices = land_use_counts[land_use_counts['percentage'] < threshold]
    main_slices = land_use_counts[land_use_counts['percentage'] >= threshold]
    
    if not small_slices.empty:
        other_sum = small_slices['count'].sum()
        other_row = pd.DataFrame([{'landuse_text': 'Other', 'count': other_sum}])
        final_counts = pd.concat([main_slices, other_row], ignore_index=True)
    else:
        final_counts = main_slices.copy()

    fig = px.pie(
        final_counts,
        names='landuse_text',
        values='count',
        hole=0.4
    )
    
    # --- MODIFIED: Move labels back outside the donut chart ---
    fig.update_traces(
        textposition='outside', 
        textinfo='percent+label', 
        textfont_size=12,
        marker=dict(line=dict(color='#FFFFFF', width=2)) # White lines for separation
    )
    
    # --- MODIFIED: Remove title, make donut bigger, and hide legend ---
    fig.update_layout(
        title_text="", # Explicitly remove the title from the plot
        margin=dict(l=20, r=20, t=20, b=20), # Reduce margins to make chart bigger
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        showlegend=False
    )
    return fig
