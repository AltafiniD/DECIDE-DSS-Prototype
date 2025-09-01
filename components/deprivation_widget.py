# components/deprivation_widget.py
import plotly.express as px
import pandas as pd

def create_deprivation_pie_chart(deprivation_df, title=""):
    """
    Creates a pie chart for household deprivation distribution.
    """
    category_col = "Household deprivation (6 categories)"

    if deprivation_df.empty or category_col not in deprivation_df.columns:
        fig = px.pie()
        fig.update_layout(
            annotations=[dict(text='No Data Available', showarrow=False, font=dict(size=16))],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Count the occurrences of each deprivation category
    category_counts = deprivation_df[category_col].value_counts().reset_index()
    category_counts.columns = [category_col, 'count']
    
    # Define a specific color map for deprivation categories
    color_map = {
        'Not deprived in any dimension': '#7cd37c',
        'Deprived in 1 dimension': '#a6d86e',
        'Deprived in 2 dimensions': '#d3dc64',
        'Deprived in 3 dimensions': '#f6d859',
        'Deprived in 4 dimensions': '#faaf48',
        'Deprived in 5 dimensions': '#f77e3c',
        'Deprived in 6 dimensions': '#f04d2f',
    }

    fig = px.pie(
        category_counts,
        names=category_col,
        values='count',
        color=category_col,
        color_discrete_map=color_map
    )
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label', 
        textfont_size=12,
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    
    fig.update_layout(
        title_text=title,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        showlegend=False,
        uniformtext_minsize=12, 
        uniformtext_mode='hide'
    )
    return fig
