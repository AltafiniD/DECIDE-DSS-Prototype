# components/slideover_panel.py

from dash import html
from .widgets import get_widgets

def create_slideover_panel(dataframes, color_map):
    """
    Creates the slide-over panel by automatically sorting and placing widgets.
    """
    widgets_data = get_widgets(dataframes, color_map)
    widgets_data.sort(key=lambda w: w['size'][0] * w['size'][1], reverse=True)
    
    # --- MODIFIED: Changed grid width from 3 to 2 for a better layout ---
    grid_width = 2
    occupied_cells = set()
    placed_widgets = []
    
    row = 0
    while widgets_data:
        col = 0
        while col < grid_width:
            if (row, col) not in occupied_cells:
                widget_to_place = None
                for i, widget in enumerate(widgets_data):
                    w_width, w_height = widget['size']
                    # Ensure width and height are integers for range()
                    w_width, w_height = int(w_width), int(w_height)
                    
                    if col + w_width <= grid_width:
                        can_place = all(
                            (row + r_offset, col + c_offset) not in occupied_cells
                            for r_offset in range(w_height)
                            for c_offset in range(w_width)
                        )
                        if can_place:
                            widget_to_place = widgets_data.pop(i)
                            break
                
                if widget_to_place:
                    w_width, w_height = widget_to_place['size']
                    content = widget_to_place['content']
                    children = [html.H4(widget_to_place.get('title', '')), html.P(content)] if isinstance(content, str) else content

                    placed_widgets.append(
                        html.Div(
                            className="widget",
                            style={
                                '--grid-col-start': col + 1, '--grid-row-start': row + 1,
                                '--grid-col-span': w_width, '--grid-row-span': w_height,
                            },
                            children=children
                        )
                    )
                    for r_offset in range(int(w_height)):
                        for c_offset in range(int(w_width)):
                            occupied_cells.add((row + r_offset, col + c_offset))
            col += 1
        row += 1

    panel = html.Div(
        id="slideover-panel",
        className="slideover-panel slideover-hidden",
        children=html.Div(className="widget-grid", children=placed_widgets)
    )
    return panel
