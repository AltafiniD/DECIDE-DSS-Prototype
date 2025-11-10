# components/buildings_at_risk_widget.py
from dash import dcc, html
import pandas as pd
from config import BUILDING_COLOR_CONFIG

def _count_hazard_classes(series):
    # count High/Medium/Low case-insensitively
    if series is None or series.empty:
        return {'High': 0, 'Medium': 0, 'Low': 0}
    s = series.dropna().astype(str).str.strip().str.capitalize()
    return {
        'High': int(s[s == 'High'].count()),
        'Medium': int(s[s == 'Medium'].count()),
        'Low': int(s[s == 'Low'].count())
    }

def _get_color_for_level(config_key, level):
    """
    Retrieves the RGB color from BUILDING_COLOR_CONFIG for a given hazard type and level.
    Returns a CSS rgb() string.
    """
    if config_key in BUILDING_COLOR_CONFIG:
        colors = BUILDING_COLOR_CONFIG[config_key].get('colors', {})
        rgba = colors.get(level.lower())
        if rgba and len(rgba) >= 3:
            return f'rgb({rgba[0]}, {rgba[1]}, {rgba[2]})'
    # Fallback colors if not found in config
    fallback = {
        'High': 'rgb(75, 0, 130)',
        'Medium': 'rgb(122, 1, 119)',
        'Low': 'rgb(247, 104, 161)'
    }
    return fallback.get(level, 'rgb(128, 128, 128)')

def create_buildings_at_risk_widget(buildings_df):
    """
    Creates three small widgets (cards) for buildings by hazard type.
    Each card is now full-width and stacked vertically.
    """
    hazard_configs = [
        {'title': 'River Flood Hazard', 'col': 'river_hazard', 'config_key': 'risk_rivers'},
        {'title': 'Surface Water Flood Hazard', 'col': 'surface_hazard', 'config_key': 'risk_watercourses'},
        {'title': 'Sea Flood Hazard', 'col': 'sea_hazard', 'config_key': 'risk_sea'}
    ]

    cards = []
    for hazard_info in hazard_configs:
        title = hazard_info['title']
        col = hazard_info['col']
        config_key = hazard_info['config_key']
        
        if buildings_df is not None and col in buildings_df.columns:
            counts = _count_hazard_classes(buildings_df[col])
            total = counts['High'] + counts['Medium'] + counts['Low']
        else:
            counts = {'High': 0, 'Medium': 0, 'Low': 0}
            total = 0

        high_color = _get_color_for_level(config_key, 'High')
        medium_color = _get_color_for_level(config_key, 'Medium')
        low_color = _get_color_for_level(config_key, 'Low')

        card = html.Div(
            # --- MODIFIED: Removed flex properties from individual card style ---
            style={
                'borderRadius': '8px', 
                'padding': '12px', 
                'background': 'white', 
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            },
            children=[
                html.Div(f"{title}", style={'fontWeight': '600', 'fontSize': '14px', 'marginBottom': '8px'}),
                html.Div(f"Total under hazard: {total:,}", style={'fontWeight': '700', 'fontSize': '16px', 'marginBottom': '10px'}),
                # --- MODIFIED: Layout of risk categories changed to horizontal flex ---
                html.Div([
                    html.Div(
                        [
                            html.Span("■ ", style={'color': high_color, 'fontSize': '16px'}),
                            html.Span(f"High: {counts['High']:,}", style={'fontSize': '13px'})
                        ]
                    ),
                    html.Div(
                        [
                            html.Span("■ ", style={'color': medium_color, 'fontSize': '16px'}),
                            html.Span(f"Medium: {counts['Medium']:,}", style={'fontSize': '13px'})
                        ]
                    ),
                    html.Div(
                        [
                            html.Span("■ ", style={'color': low_color, 'fontSize': '16px'}),
                            html.Span(f"Low: {counts['Low']:,}", style={'fontSize': '13px'})
                        ]
                    )
                ], style={'display': 'flex', 'justifyContent': 'space-around'}) # This line makes them go side-by-side and compact
            ]
        )
        cards.append(card)

    # --- MODIFIED: Changed main container to a vertical flex column ---
    content = html.Div(
        style={
            'display': 'flex', 
            'flexDirection': 'column', # Stack cards vertically
            'paddingTop': '8px',
            'gap': '10px' # Space between vertical cards
        },
        children=cards
    )
    return content
