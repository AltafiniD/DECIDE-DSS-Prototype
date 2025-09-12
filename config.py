# config.py

# Your Mapbox API key
MAPBOX_API_KEY = "pk.eyJ1IjoiaGVucnl3aWxmIiwiYSI6ImNtZDdjcHoyMjBrOWkya3NjaXcyd3p1cXkifQ.yw-wKc3DW22df0U6jo9YKQ"

# Mapbox Style Configuration
MAP_STYLES = {
    "Light": {
        "url": "mapbox://styles/mapbox/light-v9",
        "image": "assets/images/map_light.png"
    },
    "Dark": {
        "url": "mapbox://styles/mapbox/dark-v9",
        "image": "assets/images/map_dark.png"
    },
    "Streets": {
        "url": "mapbox://styles/mapbox/streets-v11",
        "image": "assets/images/map_street.png"
    },
    "Satellite": {
        "url": "mapbox://styles/mapbox/satellite-streets-v11",
        "image": "assets/images/map_satellite.png"
    }
}


# Central configuration for all flood risk layers
# FIX: Added "type": "polygon" to each flood layer so they are correctly created.
FLOOD_LAYER_CONFIG = {
    "indicators": {
        "id": "flood_indicators", "label": "Flooding Indicators",
        "file_path": "data/flood/FI01_Cardiff_Flooding_Indicators.geojson",
        "color": [0, 191, 255, 100],
        "type": "polygon"
    },
    "rivers": {
        "id": "flood_rivers", "label": "Rivers Hazard",
        "file_path": "data/flood/FPM01_Risk_Rivers_Cardiff.geojson",
        "color": [72, 61, 139, 100],
        "type": "polygon"
    },
    "sea": {
        "id": "flood_sea", "label": "Sea Hazard",
        "file_path": "data/flood/FPM01_Risk_Sea_Cardiff.geojson",
        "color": [95, 158, 160, 100],
        "type": "polygon"
    },
    "watercourses": {
        "id": "flood_watercourses", "label": "Watercourses Hazard",
        "file_path": "data/flood/FPM01_Risk_Watercourses_Cardiff.geojson",
        "color": [123, 104, 238, 100],
        "type": "polygon"
    }
}

# Configuration for dynamic building coloring
BUILDING_COLOR_CONFIG = {
    "none": { "label": "Default", "color": [220, 220, 220, 255] },
    "risk_rivers": { "label": "Risk from Rivers", "column": "river_hazard", "colors": { 
        "low": [192, 223, 213, 255], 
        "medium": [129, 191, 170, 255], 
        "high": [71, 94, 87, 255] 
    }},
    "risk_sea": { "label": "Risk from Sea", "column": "sea_hazard", "colors": { 
        "low": [149, 170, 248, 255], 
        "medium": [42, 84, 241, 255], 
        "high": [17, 34, 96, 255] 
    }},
    "risk_watercourses": { "label": "Risk from Watercourses", "column": "surface_hazard", "colors": { 
        "low": [214, 179, 255, 255], 
        "medium": [117, 0, 255, 255], 
        "high": [35, 0, 76, 255] 
    }}
}

# Columns to exclude from the dynamic network filter
NETWORK_METRICS_EXCLUDE = ['fid', 'X1', 'Y1', 'X2', 'Y2', 'Depthmap_Ref']

# Initial map view settings
INITIAL_VIEW_STATE_CONFIG = { "latitude": 51.4816, "longitude": -3.25, "zoom": 11.5, "pitch": 45, "bearing": 0 }

# --- MODIFIED: Added an 'image' key for each layer for the new buttons ---
LAYER_CONFIG = {
    "network": {
        "id": "network", "label": "Network Analysis", "file_path": "data/IR00_Integrated_Roads_Dataset.geojson",
        "type": "linestring", "visible": False, "image": "assets/images/roads.png",
        "tooltip": {"html": "<b>{metric}:</b> {value}"}
    },
    "network_outline": {
        "id": "network_outline", "label": "Network Outline", "file_path": "data/BR01_Base_Roads.geojson",
        "type": "linestring", "visible": True, "image": "assets/images/roads.png",
        "tooltip": {"text": "Road Segment"}
    },
    "stop_and_search": {
        "id": "stop_and_search", "label": "Stop & Search", "file_path": "data/SC02_Stop_and_Search.geojson",
        "type": "scatterplot", "visible": False, "image": "assets/images/stopandsearch.png",
        "tooltip": {"html": "<b>{Type}</b><br/>Object: {Object of search}<br/>Outcome: {Outcome}"}
    },
    "flooding_toggle": {
        "id": "flooding_toggle", "label": "Flooding", "type": "toggle_only", "visible": False,
        "image": "assets/images/flooding.png"
    },
    "population": {
        "id": "population", "label": "Population", "file_path": "data/POP01_Cardiff.geojson",
        "type": "polygon", "visible": False, "image": "assets/images/population.png",
        "tooltip": {"html": "<b>Residents:</b> {all_residents}<br/><b>Density:</b> {density}"}
    },
    "land_use": {
        "id": "land_use", "label": "Land Use", "file_path": "data/LU00_Land_Use_Cardiff.geojson",
        "type": "polygon", "visible": False, "image": "assets/images/land_use.png",
        "tooltip": {"html": "<b>{high_level_landuse}</b><br/>{landuse_text}"}
    },
    "buildings": {
        "id": "buildings", "label": "Buildings", "file_path": "data/BH01_Cardiff_Buildings_Hazard.geojson",
        "type": "polygon", "visible": True, "image": "assets/images/buildings.png",
        "tooltip": {"text": "Name: {NAME}\nHeight: {height}"}
    },
    "deprivation": {
        "id": "deprivation", "label": "Deprivation", "file_path": "data/HD00_OA_Household_Deprivation.geojson",
        "type": "polygon", "visible": False, "image": "assets/images/deprivation.png",
        "tooltip": {"text": "Neighbourhood: {NAME}"}
    },
    "neighbourhoods": {
        "id": "neighbourhoods", "label": "Neighbourhoods", "file_path": "data/B04_Cardiff_Communities.geojson",
        "type": "polygon", "visible": True, "image": "assets/images/neighbourhoods.png",
        "tooltip": {"text": "Neighbourhood: {NAME}"}
    },
    "crime_heatmap": {
        "id": "crime_heatmap", "label": "Crime Hexmap", "file_path": "data/SC01_Street_Crimes.geojson",
        "type": "hexagon", "visible": False,
        "tooltip": {"html": "<b>Number of crimes:</b> {elevationValue}"}
    },
    "crime_points": {
        "id": "crime_points", "label": "Crime Points", "file_path": "data/SC01_Street_Crimes.geojson",
        "type": "scatterplot", "visible": False,
        "tooltip": {"text": "Crime Type: {Crime type}\nLocation: {Location}"}
    }
}
