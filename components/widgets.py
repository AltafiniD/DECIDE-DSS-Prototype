# components/widgets.py
from dash import dcc, html
import pandas as pd
from .crime_widget import create_crime_histogram_figure

def get_widgets(dataframes, color_map):
    """
    Defines a list of all widgets to be displayed in the slide-over panel.
    """
    # Use one of the new crime dataframes
    crime_df = dataframes.get('crime_points', pd.DataFrame())
    initial_crime_fig = create_crime_histogram_figure(crime_df, color_map)

    crime_statistics_widget = {
        "size": (3, 3),
        "content": [
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'},
                children=[
                    dcc.Markdown(id="crime-widget-title", children="#### Crime Statistics for Cardiff"),
                    html.Button("Clear Selection", id="clear-crime-filter-btn", n_clicks=0, style={'fontSize': '12px'})
                ]
            ),
            dcc.Graph(id="crime-bar-chart", figure=initial_crime_fig, style={'height': '85%'})
        ]
    }
    widgets = [
        crime_statistics_widget,
        { "size": (2, 2), "title": "Medium Widget (2x2)", "content": "A standard medium-sized widget." },
        { "size": (1, 2), "title": "Slim Widget (1x2)", "content": "A slim, tall widget." },
        { "size": (1, 1), "title": "Small (1x1)", "content": "A small widget." },
    ]
    return widgets
