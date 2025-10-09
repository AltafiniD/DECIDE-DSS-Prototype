# components/flood_risk_widget.py
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from config import BUILDING_COLOR_CONFIG

def create_flood_risk_chart(df, hazard_column, title="Flood Hazard Distribution"):
    """
    Returns stacked horizontal bar chart(s) for flood hazard distribution of buildings.
    MODIFIED: Reverts to a contiguous stacked bar (High, Medium, Low) normalized to 100%.
    X-axis uses 5% tick intervals. Spacing is increased to prevent subplot title overlap.
    Hover data is ensured for 0% segments.
    """
    if df is None or df.empty:
        fig = go.Figure()
        fig.update_layout(title="No building data for this selection", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig

    hazard_list = hazard_column if isinstance(hazard_column, (list, tuple)) else [hazard_column]
    valid_hazards = [h for h in hazard_list if h in df.columns]
    if not valid_hazards:
        fig = go.Figure()
        fig.update_layout(title="No valid hazard columns selected", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig

    hazard_key_map = {'surface_hazard': 'risk_watercourses', 'river_hazard': 'risk_rivers', 'sea_hazard': 'risk_sea'}
    # Order for plotting all 'At Hazard' levels
    preferred_order = ['High', 'Medium', 'Low'] 
    
    all_hazard_titles = []
    for h in hazard_list:
        if h == 'surface_hazard': all_hazard_titles.append("Surface Flooding")
        elif h == 'river_hazard': all_hazard_titles.append("River Flooding")
        elif h == 'sea_hazard': all_hazard_titles.append("Sea Flooding")
        else: all_hazard_titles.append(h)

    num_hazards = len(hazard_list)
    fig = make_subplots(
        rows=num_hazards, cols=1,
        shared_xaxes=True,
        subplot_titles=all_hazard_titles,
        vertical_spacing=0.20
    )

    row_data_map = {}
    
    X_AXIS_MAX = 100.0
    MIN_HOVER_LENGTH = 0.01
    
    # -------------------------------------------------------------
    # --- Data Processing: Filter and Recalculate Percentages ---
    # -------------------------------------------------------------
    for hazard in hazard_list:
        if hazard in valid_hazards:
            raw_counts = df[hazard].fillna('Not at hazard').value_counts().reset_index()
            raw_counts.columns = ['level', 'count']
            raw_counts['level'] = raw_counts['level'].astype(str).str.strip().str.capitalize()
            
            at_hazard_counts = raw_counts[raw_counts['level'].isin(preferred_order)].copy()
            not_at_hazard_count = raw_counts[raw_counts['level'] == 'Not at hazard']['count'].sum()
            
            total_at_hazard = at_hazard_counts['count'].sum()
            total_all = raw_counts['count'].sum()

            if total_at_hazard > 0:
                # Recalculate percentages relative to the total *at hazard*
                at_hazard_counts['percentage'] = (at_hazard_counts['count'] / total_at_hazard) * 100
                at_hazard_counts['total_count'] = total_all
                
                at_hazard_counts['level'] = pd.Categorical(at_hazard_counts['level'], categories=preferred_order, ordered=True)
                counts_for_plot = at_hazard_counts.sort_values('level').reset_index(drop=True)
            else:
                counts_for_plot = pd.DataFrame({
                    'level': preferred_order, 'count': 0, 'percentage': 0.0, 'total_count': total_all
                })
                
            row_data_map[hazard] = {'counts': counts_for_plot, 'not_at_hazard_count': not_at_hazard_count}
        else:
            row_data_map[hazard] = {'counts': pd.DataFrame(), 'not_at_hazard_count': 0}

    # -------------------------------------------------------------
    # --- Plotting Loop (Contiguous Bar) ---
    # -------------------------------------------------------------
    for i, hazard in enumerate(hazard_list, 1):
        data = row_data_map[hazard]
        counts = data['counts']
        hazard_key = hazard_key_map.get(hazard)
        
        color_map = {}
        if hazard_key and hazard_key in BUILDING_COLOR_CONFIG:
            colors_rgba = BUILDING_COLOR_CONFIG[hazard_key].get('colors', {})
            for level, rgba in colors_rgba.items():
                color_map[level.capitalize()] = f'rgb({rgba[0]}, {rgba[1]}, {rgba[2]})'
        
        total_at_hazard_buildings = counts['count'].sum()
        
        if total_at_hazard_buildings == 0:
             fig.add_trace(go.Bar(y=[''], x=[100], orientation='h', name='No Data', marker=dict(color='lightgrey'), hoverinfo='none', showlegend=False), row=i, col=1)
        
        # --- Plotting High, Medium, Low contiguously ---
        for level_to_plot in preferred_order:
            row = counts[counts['level'] == level_to_plot]
            if not row.empty:
                row = row.iloc[0]
                percentage = row['percentage']
                count = row['count']
                
                # Trace length: if percentage is exactly 0, use MIN_HOVER_LENGTH for hoverability.
                # If percentage is > 0 (even if tiny), use its actual value.
                trace_length = percentage if percentage >= 0.01 else MIN_HOVER_LENGTH
                
                if count >= 0:
                    overall_percent = count / row["total_count"] * 100 if row["total_count"] > 0 else 0.0
                    
                    # Hover template uses the actual percentage and count
                    hovertemplate = (
                        f'{level_to_plot}: {count:,.0f} buildings ({percentage:.1f}% of at-risk)<br>'
                        f'Overall: {overall_percent:.1f}%<extra></extra>'
                    )
                    
                    # Marker color: Only fully transparent if percentage is exactly 0.
                    marker_color = color_map.get(level_to_plot)
                    if percentage == 0:
                         marker_color = 'rgba(0,0,0,0)'

                    fig.add_trace(
                        go.Bar(
                            y=[''], x=[trace_length], orientation='h', name=level_to_plot,
                            marker=dict(color=marker_color),
                            hovertemplate=hovertemplate, showlegend=False,
                            customdata=[count]
                        ),
                        row=i, col=1
                    )

        # 4. Legend positioned relative to the subplot 
        if hazard in valid_hazards:
            present_labels = [l for l in preferred_order if l in color_map]
            
            num_labels = len(present_labels)
            x_step = min(0.22, 0.9 / max(num_labels, 1))
            x_start = 0.05
            
            legend_y = 1.15 # Adjusted y position for better vertical separation
            
            for j, lbl in enumerate(present_labels):
                x_pos = x_start + j * x_step
                block = "■"
                color = color_map.get(lbl, 'lightgrey')
                fig.add_annotation(
                    x=x_pos, y=legend_y,
                    xref='paper', yref=f'y{i}', 
                    text=f"<span style='color:{color}; font-size:12px'>{block}</span> <span style='font-size:10px'>{lbl}</span>",
                    showarrow=False, align='left', xanchor='left', yanchor='middle', font=dict(color='black')
                )

        # 5. Fix axis range and ticks
        fig.update_xaxes(range=[0, X_AXIS_MAX], 
            ticks="outside", 
            tickformat=".0f%", 
            dtick=5, 
            showgrid=True, 
            gridcolor='rgba(128,128,128,0.2)', 
            row=i, col=1)
        fig.update_yaxes(showticklabels=False, showgrid=False, row=i, col=1)

    # --- Final Layout Adjustments ---
    base_height_per_hazard = 130
    title_height = 60
    total_height = title_height + num_hazards * base_height_per_hazard 

    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=title_height, b=20), 
        barmode='stack',
        showlegend=False,
        height=total_height
    )
    
    return fig
