# components/land_use_widget.py
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_land_use_donut_chart(land_use_df, title=""):
    """
    Creates a stacked horizontal bar chart for land use distribution using plotly.express.
    """
    if land_use_df.empty or 'landuse_text' not in land_use_df.columns:
        fig = go.Figure()
        fig.update_layout(annotations=[dict(text='No Data Available', showarrow=False, font=dict(size=16))])
        return fig

    # --- Data processing logic (unchanged) ---
    land_use_counts = land_use_df['landuse_text'].value_counts().reset_index()
    land_use_counts.columns = ['landuse_text', 'count']
    
    color_df = land_use_df[['landuse_text', 'color']].drop_duplicates(subset=['landuse_text'])
    other_color_rgba = [128, 128, 128, 160]

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

    final_counts = pd.merge(final_counts, color_df, on='landuse_text', how='left')
    final_counts['color'] = final_counts['color'].apply(lambda x: x if isinstance(x, list) else other_color_rgba)
    
    # --- NEW: Rebuilding the figure with Plotly Express ---
    
    # Create a color map for plotly express to use
    color_map = {
        row['landuse_text']: f'rgba({row["color"][0]},{row["color"][1]},{row["color"][2]},{row["color"][3]/255})'
        for _, row in final_counts.iterrows()
    }

    # Add a constant column for the y-axis to force all segments onto a single bar
    final_counts['y_axis'] = 'Land Use'

    fig = px.bar(
        final_counts,
        x='percentage',
        y='y_axis',
        color='landuse_text',
        orientation='h',
        color_discrete_map=color_map,
        custom_data=['landuse_text']  # This correctly passes the data for click events
    )

    # Add the percentage text inside each segment
    fig.update_traces(
        texttemplate='%{x:.1f}%', 
        textposition='inside',
        insidetextanchor='middle'
    )

    # --- Layout updates to style the chart ---
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 100], title=''),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=80),
        height=220,
        legend=dict(
            title_text='',
            orientation="h",
            yanchor="bottom", y=-0.5,
            xanchor="center", x=0.5,
            traceorder='normal',
            itemwidth=40
        ),
        showlegend=True,
        clickmode='event'
    )
    return fig

