# config.py

# Your Mapbox API key
MAPBOX_API_KEY = "pk.eyJ1IjoiaGVucnl3aWxmIiwiYSI6ImNtZDdjcHoyMjBrOWkya3NjaXcyd3p1cXkifQ.yw-wKc3DW22df0U6jo9YKQ"

# Mapbox Style Configuration
MAP_STYLES = {
    "Light": "mapbox://styles/mapbox/light-v9",
    "Dark": "mapbox://styles/mapbox/dark-v9",
    "Streets": "mapbox://styles/mapbox/streets-v11",
    "Satellite": "mapbox://styles/mapbox/satellite-streets-v11"
}

NETWORK_METRICS_EXCLUDE = ['fid', 'X1', 'Y1', 'X2', 'Y2', 'Depthmap_Ref']

# Initial map view settings
INITIAL_VIEW_STATE_CONFIG = {
    "latitude": 51.4816,
    "longitude": -3.1791,
    "zoom": 12,
    "pitch": 45, # Keep a default pitch
    "bearing": 0,
}

# --- Layer Configuration ---
# THE FIX: Replaced garbled characters with standard emojis.
LAYER_CONFIG = {
    "buildings": {
        "id": "buildings", "label": "Buildings", "emoji": "🏢", "file_path": "data/BS01_Cardiff_Buildings.geojson",
        "type": "polygon", "visible": False, "tooltip": {"text": "Name: {NAME}\nHeight: {height}"}
    },
    "neighbourhoods": {
        "id": "neighbourhoods", "label": "Neighbourhoods", "emoji": "🏘️", "file_path": "data/B04_Cardiff_Communities.geojson",
        "type": "polygon", "visible": False, "tooltip": {"text": "Neighbourhood: {NAME}"}
    },
    "flooding": {
        "id": "flooding", "label": "Flooding", "emoji": "🌊", "file_path": "data/FI01_Cardiff_Flooding_Indicators.geojson",
        "type": "polygon", "visible": False,
    },
    "crime_heatmap": {
        "id": "crime_heatmap", "label": "Hexmap", "emoji": "🟥", "file_path": "data/SC01_Street_Crimes.geojson",
        "type": "hexagon", "visible": False, "tooltip": {"html": "<b>Number of crimes:</b> {elevationValue}"}
    },
    "crime_points": {
        "id": "crime_points", "label": "Points", "emoji": "📍", "file_path": "data/SC01_Street_Crimes.geojson",
        "type": "scatterplot", "visible": False, "tooltip": {"text": "Crime Type: {Crime type}\nLocation: {Location}"}
    },
    "network": {
        "id": "network", "label": "Network Analysis", "emoji": "🕸️", "file_path": "data/ASA02_Cardiff.geojson",
        "type": "linestring", "visible": False, "tooltip": {"html": "<b>{metric}:</b> {value}"}
    }
}
