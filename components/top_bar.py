# # components/top_bar.py

# from dash import dcc, html
# import pandas as pd

# def create_top_bar(crime_df, network_df):
#     """
#     Creates the top filter bar with sliders, a dropdown, and an apply button.
#     """
#     # --- Time Filter for Crimes ---
#     crime_df['Month_dt'] = pd.to_datetime(crime_df['Month'], format='%Y-%m', errors='coerce')
#     unique_months = sorted(crime_df['Month_dt'].dropna().unique())
#     month_map = {i: month.strftime('%Y-%m') for i, month in enumerate(unique_months)}
    
#     time_marks = {}
#     if len(unique_months) > 0:
#         time_marks[0] = unique_months[0].strftime('%b %Y')
#         if len(unique_months) > 1:
#             time_marks[len(unique_months) - 1] = unique_months[-1].strftime('%b %Y')

#     time_slider = dcc.RangeSlider(
#         id='time-filter-slider',
#         min=0, max=len(unique_months) - 1 if unique_months else 0,
#         value=[0, len(unique_months) - 1 if unique_months else 0],
#         marks=time_marks, step=1,
#         className="top-bar-slider",
#         tooltip={"placement": "bottom", "always_visible": False},
#         disabled=not bool(unique_months)
#     )

#     # --- NAIN Filter for Network ---
#     if 'NAIN' in network_df.columns:
#         network_df['NAIN'] = pd.to_numeric(network_df['NAIN'], errors='coerce')
#         nain_min, nain_max = network_df['NAIN'].min(), network_df['NAIN'].max()
#     else:
#         nain_min, nain_max = 0, 1.5

#     nain_slider = dcc.RangeSlider(
#         id='nain-filter-slider',
#         min=nain_min, max=nain_max, step=0.01,
#         value=[nain_min, nain_max],
#         marks={f'{nain_min:.1f}': f'{nain_min:.1f}', f'{nain_max:.1f}': f'{nain_max:.1f}'},
#         className="top-bar-slider",
#         tooltip={"placement": "bottom", "always_visible": False},
#         disabled=pd.isna(nain_min) or pd.isna(nain_max)
#     )

#     # --- Crime Type Filter ---
#     all_crime_types = sorted(crime_df['Crime type'].dropna().unique())
#     crime_type_dropdown = dcc.Dropdown(
#         id='crime-type-filter-dropdown',
#         options=[{'label': crime, 'value': crime} for crime in all_crime_types],
#         value=[], 
#         multi=True,
#         placeholder="Filter by Crime Type (all shown by default)"
#     )

#     panel = html.Div(
#         className="top-bar-container",
#         children=[
#             html.Div(className="top-bar-filter", children=[
#                 html.Label("Time Range (Crimes)"),
#                 time_slider
#             ]),
#             html.Div(className="top-bar-filter", children=[
#                 html.Label("NAIN Range (Network)"),
#                 nain_slider
#             ]),
#             html.Div(className="top-bar-filter", children=[
#                 html.Label("Crime Types"),
#                 crime_type_dropdown
#             ]),
#             # Add the apply button
#             html.Button("Apply Filters", id="apply-filters-btn", n_clicks=0, className="apply-filters-button")
#         ]
#     )
    
#     return panel, month_map
