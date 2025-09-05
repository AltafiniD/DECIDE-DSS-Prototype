# components/slideover_panel.py

from dash import html

# --- MODIFIED: The function no longer needs dataframes or color_map arguments ---
def create_slideover_panel():
    """
    Creates the slide-over panel with an empty container for dynamic widgets.
    The content will be populated by a callback.
    """
    panel = html.Div(
        id="slideover-panel",
        className="slideover-panel slideover-hidden",
        # --- MODIFIED: The inner div now has an ID and is initially empty ---
        children=html.Div(id="widget-grid-container", className="widget-grid")
    )
    return panel
