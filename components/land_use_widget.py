# components/land_use_widget.py
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import textwrap

# --- SPACING CONTROLS ---
# 1. Increased space for the detailed land use legend
LAND_USE_LEGEND_TOP_MARGIN_PX = 250 
# 2. Margin for the high level chart is set to 0 (Test)
HIGH_LEVEL_LEGEND_TOP_MARGIN_PX = 0
# ------------------------

def create_land_use_chart(land_use_df, title=""):
    """
    Creates a stacked horizontal bar chart for land use distribution using plotly.express.
    Ensures all legend items appear regardless of data presence by using an exhaustive color_discrete_map.
    """
    if land_use_df.empty or 'landuse_text' not in land_use_df.columns:
        fig = go.Figure()
        fig.update_layout(annotations=[dict(text='No Data Available', showarrow=False, font=dict(size=16))])
        return fig

    # Capture ALL unique land use types and their associated colors from the input DF.
    color_df = land_use_df[['landuse_text', 'color']].drop_duplicates(subset=['landuse_text']).copy()
    other_color_rgba = [128, 128, 128, 160]
    
    color_map = {}
    
    # 1. Add all actual categories from the original data to the map
    for _, row in color_df.iterrows():
        # Ensure the color is treated as a list of integers before formatting
        color_rgba = row['color'] if isinstance(row['color'], list) else other_color_rgba
        color_map[row['landuse_text']] = f'rgba({color_rgba[0]},{color_rgba[1]},{color_rgba[2]},{color_rgba[3]/255})'

    color_map['Other'] = f'rgba({other_color_rgba[0]},{other_color_rgba[1]},{other_color_rgba[2]},{other_color_rgba[3]/255})'
    # --- END EXHAUSTIVE COLOR MAP CREATION ---

    # Data processing logic (aggregation for charting)
    land_use_counts = land_use_df['landuse_text'].value_counts().reset_index()
    land_use_counts.columns = ['landuse_text', 'count']
    total_count = land_use_counts['count'].sum()
    land_use_counts['percentage'] = (land_use_counts['count'] / total_count) * 100 if total_count > 0 else 0
    threshold = 2.0
    small_slices = land_use_counts[land_use_counts['percentage'] < threshold]
    main_slices = land_use_counts[land_use_counts['percentage'] >= threshold]
    
    if not small_slices.empty:
        other_sum = small_slices['count'].sum()
        other_row = pd.DataFrame([{'landuse_text': 'Other', 'count': other_sum, 'percentage': (other_sum / total_count) * 100}])
        final_counts = pd.concat([main_slices, other_row], ignore_index=True)
    else:
        final_counts = main_slices.copy()
        
    final_counts['y_axis'] = 'Land Use'

    fig = px.bar(
        final_counts, x='percentage', y='y_axis', color='landuse_text',
        orientation='h', 
        color_discrete_map=color_map,
        custom_data=['landuse_text']
    )
    fig.update_traces(texttemplate='%{x:.1f}%', textposition='inside', insidetextanchor='middle')
    
    chart_height_px = 100 
    xaxis_height_px = 25 
    total_height_px = chart_height_px + LAND_USE_LEGEND_TOP_MARGIN_PX + xaxis_height_px 
    
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)', zeroline=False, showticklabels=True, range=[0, 100], title_text='', ticks="outside", tickformat=".0f%", dtick=20),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        # Set the larger top margin to reserve space for the legend
        margin=dict(l=10, r=10, t=LAND_USE_LEGEND_TOP_MARGIN_PX, b=xaxis_height_px), 
        height=total_height_px,
        showlegend=True,
        # Configuration for top legend placement
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.0, 
            xanchor="center",
            x=0.5,
            traceorder='normal',
            font=dict(size=12, color="#333"),
            title=''
        )
    )
    return fig

def create_high_level_land_use_chart(land_use_df, title=""):
    """
    Creates a stacked horizontal bar chart for high-level land use distribution.
    Ensures all legend items appear by using the full hardcoded color map.
    """
    if land_use_df.empty or 'high_level_landuse' not in land_use_df.columns:
        fig = go.Figure()
        fig.update_layout(annotations=[dict(text='No Data Available', showarrow=False, font=dict(size=16))])
        return fig

    # Data processing logic (aggregation for charting)
    high_level_counts = land_use_df['high_level_landuse'].value_counts().reset_index()
    high_level_counts.columns = ['high_level_landuse', 'count']
    total_count = high_level_counts['count'].sum()
    high_level_counts['percentage'] = (high_level_counts['count'] / total_count) * 100 if total_count > 0 else 0
    high_level_counts = high_level_counts.sort_values('percentage', ascending=False)
    
    high_level_colors = {
        'Natural': 'rgba(100, 180, 100, 0.8)', 
        'Man Made': 'rgba(140, 140, 140, 0.8)', 
        'Agricultural': 'rgba(150, 180, 100, 0.8)', 
        'Managed': 'rgba(100, 200, 150, 0.8)'
    }
    
    color_map = high_level_colors.copy()
    
    fallback_color = 'rgba(128, 128, 128, 0.6)'
    for category in high_level_counts['high_level_landuse'].unique():
        if category not in color_map:
            color_map[category] = fallback_color
    
    high_level_counts['y_axis'] = 'High-Level Land Use'

    fig = px.bar(
        high_level_counts, x='percentage', y='y_axis', color='high_level_landuse',
        orientation='h', 
        color_discrete_map=color_map, # Use the exhaustive map
        custom_data=['high_level_landuse']
    )
    fig.update_traces(texttemplate='%{x:.1f}%', textposition='inside', insidetextanchor='middle')
    
    chart_height_px = 100
    total_height_px = chart_height_px + 25 # Base height (chart + x-axis approx.)
    
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)', zeroline=False, showticklabels=True, range=[0, 100], title_text='', ticks="outside", tickformat=".0f%", dtick=20),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        # Set all margins to 0 for the test
        margin=dict(l=0, r=0, t=0, b=0),
        height=total_height_px, 
        showlegend=True,
        # Configuration for top legend placement
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            xanchor="center",
            x=0.5,
            traceorder='normal',
            font=dict(size=12, color="#333"),
            title=''
        )
    )
    return fig
    # Note: Labels that have low counts in land use are grouped into 'Other' for clarity.

