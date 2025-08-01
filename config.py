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

# Central configuration for all flood risk layers
FLOOD_LAYER_CONFIG = {
    "indicators": {
        "id": "flood_indicators", "label": "Flooding Indicators",
        "file_path": "data/flood/FI01_Cardiff_Flooding_Indicators.geojson",
        "color": [0, 191, 255, 100]
    },
    "rivers": {
        "id": "flood_rivers", "label": "Risk from Rivers",
        "file_path": "data/flood/FPM01_Risk_Rivers_Cardiff.geojson",
        "color": [72, 61, 139, 100]
    },
    "sea": {
        "id": "flood_sea", "label": "Risk from Sea",
        "file_path": "data/flood/FPM01_Risk_Sea_Cardiff.geojson",
        "color": [95, 158, 160, 100]
    },
    "watercourses": {
        "id": "flood_watercourses", "label": "Risk from Watercourses",
        "file_path": "data/flood/FPM01_Risk_Watercourses_Cardiff.geojson",
        "color": [123, 104, 238, 100]
    }
}

# --- NEW: Configuration for dynamic building coloring ---
# Defines the dropdown options and the color scales for each risk type.
# NOTE: We are assuming the column names in your buildings data are 'Risk_Rivers' and 'Risk_Sea'.
# If they are different, you can easily change them here.
BUILDING_COLOR_CONFIG = {
    "none": {
        "label": "Default",
        "color": [220, 220, 220, 180] # Default grey color
    },
    "risk_rivers": {
        "label": "Risk from Rivers",
        "column": "Rivers_risk",
        "colors": {
            "low": [132, 124, 179, 180],    # Lighter DarkSlateBlue
            "medium": [72, 61, 139, 180],  # Opaque DarkSlateBlue
            "high": [42, 31, 99, 180]      # Darker DarkSlateBlue
        }
    },
    "risk_sea": {
        "label": "Risk from Sea",
        "column": "Sea_risk",
        "colors": {
            "low": [155, 198, 200, 180],    # Lighter CadetBlue
            "medium": [95, 158, 160, 180], # Opaque CadetBlue
            "high": [55, 118, 120, 180]     # Darker CadetBlue
        }
    }
}

# Columns to exclude from the dynamic network filter
NETWORK_METRICS_EXCLUDE = ['fid', 'X1', 'Y1', 'X2', 'Y2', 'Depthmap_Ref']

# Initial map view settings
INITIAL_VIEW_STATE_CONFIG = {
    "latitude": 51.4816, "longitude": -3.1791, "zoom": 12, "pitch": 45, "bearing": 0,
}

# Layer Configuration
LAYER_CONFIG = {
    "stop_and_search": {
        "id": "stop_and_search", "label": "Stop & Search", "file_path": "data/SC02_Stop_and_Search.geojson",
        "type": "scatterplot", "visible": False,
        "tooltip": {"html": "<b>{Type}</b><br/>Object: {Object of search}<br/>Outcome: {Outcome}"}
    },
    "flooding_toggle": {
        "id": "flooding_toggle", "label": "Flooding", "type": "toggle_only", "visible": False
    },
    "population": {
        "id": "population", "label": "Population", "file_path": "data/POP01_Cardiff.geojson",
        "type": "polygon", "visible": False,
        "tooltip": {"html": "<b>Residents:</b> {all_residents}<br/><b>Density:</b> {density}"}
    },
    "land_use": {
        "id": "land_use", "label": "Land Use", "file_path": "data/LU00_Land_Use_Cardiff.geojson",
        "type": "polygon", "visible": False,
        "tooltip": {"html": "<b>{high_level_landuse}</b><br/>{landuse_text}"}
    },
    "buildings": {
        "id": "buildings", "label": "Buildings", "file_path": "data/IB01_Integrated_Buildings_Dataset.geojson",
        "type": "polygon", "visible": False,
        "tooltip": {"text": "Name: {NAME}\nHeight: {height}"}
    },
    "deprivation": {
        "id": "deprivation", "label": "Deprivation", "file_path": "data/HD00_OA_Household_Deprivation.geojson",
        "type": "polygon", "visible": False,
        "tooltip": {"text": "Neighbourhood: {NAME}"}
    },
    "neighbourhoods": {
        "id": "neighbourhoods", "label": "Neighbourhoods", "file_path": "data/B04_Cardiff_Communities.geojson",
        "type": "polygon", "visible": True,
        "tooltip": {"text": "Neighbourhood: {NAME}"}
    },
    "crime_heatmap": {
        "id": "crime_heatmap", "label": "Crime Heatmap", "file_path": "data/SC01_Street_Crimes.geojson",
        "type": "hexagon", "visible": False,
        "tooltip": {"html": "<b>Number of crimes:</b> {elevationValue}"}
    },
    "crime_points": {
        "id": "crime_points", "label": "Crime Points", "file_path": "data/SC01_Street_Crimes.geojson",
        "type": "scatterplot", "visible": False,
        "tooltip": {"text": "Crime Type: {Crime type}\nLocation: {Location}"}
    },
    "network": {
        "id": "network", "label": "Network Analysis", "file_path": "data/ASA02_Cardiff.geojson",
        "type": "linestring", "visible": False,
        "tooltip": {"html": "<b>{metric}:</b> {value}"}
    }
}
