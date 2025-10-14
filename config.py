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
        "color": [95, 158, 160, 100], 
        "type": "polygon"
    },
    "sea": {
        "id": "flood_sea", "label": "Sea Hazard",
        "file_path": "data/flood/FPM01_Risk_Sea_Cardiff.geojson",
        "color": [65, 105, 225, 100],
        "type": "polygon"
    },
    "watercourses": {
        "id": "flood_watercourses", "label": "Surface Water Hazard",
        "file_path": "data/flood/FPM01_Risk_Watercourses_Cardiff.geojson",
        "color": [28, 92, 120, 100],
        "type": "polygon"
    }
}

# New dictionary to store the base RGB (excluding alpha) for gradient generation
FLOOD_BASE_COLORS = {
    # Keys match the metric suffixes requested: "_rivers_risk", "_sea_risk", "_surface_risk"
    "rivers_risk": [95, 158, 160],
    "sea_risk": [65, 105, 225],
    "surface_risk": [28, 92, 120]
}

# Configuration for dynamic building coloring
# UPDATED: Colors now derived from FLOOD_LAYER_CONFIG base colors
BUILDING_COLOR_CONFIG = {
    "none": { "label": "Default", "color": [220, 220, 220, 255] },
    "risk_rivers": { 
        "label": "Risk from Rivers", 
        "column": "river_hazard", 
        "colors": { 
            "low": [160, 200, 202, 255], 
            "medium": [125, 180, 182, 255],
            "high": [95, 158, 160, 255]
        }
    },
    "risk_sea": { 
        "label": "Risk from Sea", 
        "column": "sea_hazard", 
        "colors": { 
            "low": [140, 180, 255, 255],       
            "medium": [100, 140, 240, 255],        
            "high": [65, 105, 225, 255]  
        }
    },
    "risk_watercourses": { 
        "label": "Risk from Surface Water", 
        "column": "surface_hazard", 
        "colors": { 
            "low": [120, 180, 205, 255],      
            "medium": [75, 135, 165, 255],    
            "high": [28, 92, 120, 255]        
        }
    }
}

# --- NEW: Centralized color maps for crime data ---

# Configuration for stop and search 'Object of search' categories
STOP_AND_SEARCH_COLOR_MAP = {
    'Controlled drugs': "#00AA39",  # Green
    'Offensive weapons': '#3498DB',  # Blue
    'Stolen goods': '#F39C12',  # Orange
    'Article for use in theft': '#9B59B6',  # Purple (Corrected to singular)
    'Articles for use in criminal damage': '#34495E',  # Dark Blue-Gray
    'Firearms': '#1ABC9C',  # Teal
    'Anything to threaten or harm anyone': '#E67E22',  # Dark Orange
    'Evidence of offences under the Act': '#95A5A6',  # Gray
    'Psychoactive substances': '#2ECC71',  # Light Green
    'Fireworks': '#16A085',  # Dark Teal
    'Game or poaching equipment': '#D35400',  # Dark Orange-Red
    'Goods on which duty has not been paid etc.': '#FF5733', # Red-Orange
    'None': '#A9A9A9' # Dark Gray for null/missing values
}

# Configuration for crime categories
CRIME_COLOR_MAP = {
    'Violence and sexual offences': '#E74C3C', # Red
    'Anti-social behaviour': '#2ECC71',       # Green
    'Public order': '#3498DB',                # Blue
    'Criminal damage and arson': '#F1C40F',    # Yellow
    'Vehicle crime': '#9B59B6',               # Purple
    'Other theft': '#E67E22',                 # Dark Orange
    'Shoplifting': '#1ABC9C',                 # Teal
    'Burglary': '#34495E',                    # Dark Blue-Gray
    'Drugs': '#C0392B',                       # Dark Red
    'Robbery': '#A93226',                     # Darker Red
    'Theft from the person': '#FF5733',        # Red-Orange
    'Bicycle theft': '#27AE60',               # Medium Green
    'Possession of weapons': '#7F8C8D',       # Gray
    'Other crime': '#A9A9A9',                 # Dark Gray
    'None': '#A9A9A9'                         # For null/missing values
}

# Columns to exclude from the dynamic network filter
NETWORK_METRICS_EXCLUDE = ['fid', 'X1', 'Y1', 'X2', 'Y2', 'Depthmap_Ref']

# Initial map view settings
INITIAL_VIEW_STATE_CONFIG = { "latitude": 51.4950, "longitude": -3.20, "zoom": 11.5, "pitch": 45, "bearing": 0 }

# --- MODIFIED: Added an 'image' key for each layer for the new buttons ---
LAYER_CONFIG = {
    "neighbourhoods": {
        "id": "neighbourhoods", "label": "Neighbourhoods", "file_path": "data/B04_Cardiff_Communities.geojson",
        "type": "polygon", "visible": True, "image": "assets/images/neighbourhoods.png",
        "tooltip": {"text": "Neighbourhood: {NAME}"}
    },
    "network_outline": {
        "id": "network_outline", "label": "Road Network", "file_path": "data/BR01_Base_Roads.geojson",
        "type": "linestring", "visible": True, "image": "assets/images/roads.png",
        "tooltip": {"text": "Road Segment"},
    },
    "buildings": {
        "id": "buildings", "label": "Buildings", "file_path": "data/BH01_Cardiff_Buildings_Hazard.geojson",
        "type": "polygon", "visible": True, "image": "assets/images/buildings.png",
        "tooltip": {"text": "Name: {NAME}\nHeight: {height}"}
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
    "network": {
        "id": "network", "label": "Network Analysis", "file_path": "data/IR00_Integrated_Roads_Dataset.geojson",
        "type": "linestring", "visible": False, "image": "assets/images/roads.png",
        "tooltip": {"html": "<b>{metric}:</b> {value}"}
    },
    "flooding_toggle": {
        "id": "flooding_toggle", "label": "Flooding", "type": "toggle_only", "visible": False,
        "image": "assets/images/flooding.png"
    },
    "deprivation": {
        "id": "deprivation", "label": "Deprivation Index", "file_path": "data/HD00_OA_Household_Deprivation.geojson",
        "type": "polygon", "visible": False, "image": "assets/images/deprivation.png",
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
    },
     "stop_and_search": {
        "id": "stop_and_search", "label": "Stop & Search", "file_path": "data/SC02_Stop_and_Search.geojson",
        "type": "scatterplot", "visible": False, "image": "assets/images/stopandsearch.png",
        "tooltip": {"html": "<b>{Type}</b><br/>Object: {Object of search}<br/>Outcome: {Outcome}"}
    }
}