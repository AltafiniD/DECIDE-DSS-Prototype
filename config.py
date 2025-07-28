# config.py

# Your Mapbox API key
MAPBOX_API_KEY = "pk.eyJ1IjoiaGVucnl3aWxmIiwiYSI6ImNtZDdjcHoyMjBrOWkya3NjaXcyd3p1cXkifQ.yw-wKc3DW22df0U6jo9YKQ"

# Initial map view settings
INITIAL_VIEW_STATE_CONFIG = {
    "latitude": 51.4816,
    "longitude": -3.1791,
    "zoom": 12,
    "pitch": 0, # Start at a 2D angle
    "bearing": 0,
}

# --- Layer Configuration ---
LAYER_CONFIG = {
    "buildings": {
        "id": "buildings", "label": "Buildings", "file_path": "data/BS01_Cardiff_Buildings.geojson",
        "type": "polygon", "visible": False,
        "tooltip": {"text": "Name: {NAME}\nHeight: {height}"}
    },
    "neighbourhoods": {
        "id": "neighbourhoods", "label": "Neighbourhoods", "file_path": "data/B02_Cardiff_Neighbourhoods.geojson",
        "type": "polygon", "visible": False,
        "tooltip": {"text": "Neighbourhood: {NAME}"}
    },
    "flooding": {
        "id": "flooding", "label": "Flooding", "file_path": "data/FI01_Cardiff_Flooding_Indicators.geojson",
        "type": "polygon", "visible": False,
    },
    "crime": {
        "id": "crime", "label": "Street Crimes", "file_path": "data/SC01_Street_Crimes.geojson",
        "type": "scatterplot", "visible": False,
        "tooltip": {"text": "Crime Type: {Crime type}\nLocation: {Location}"}
    },
    "network": {
        "id": "network", "label": "Network Analysis", "file_path": "data/ASA02_Cardiff.geojson",
        "type": "linestring", "visible": False,
        "tooltip": {"text": "Connectivity: {Connectivity}\nNAIN: {NAIN}"}
    }
}
