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
# UPDATED: Granular layers for each hazard level (High, Medium, Low)
FLOOD_LAYER_CONFIG = {
    "rivers_high": {
        "id": "flood_rivers_high", "label": "Rivers - High Hazard",
        "file_path": "data/flood/FPM01_Risk_Rivers_Cardiff.geojson",
        "hazard_level": "high",
        "hazard_type": "rivers_risk",
        "type": "polygon"
    },
    "rivers_medium": {
        "id": "flood_rivers_medium", "label": "Rivers - Medium Hazard",
        "file_path": "data/flood/FPM01_Risk_Rivers_Cardiff.geojson",
        "hazard_level": "medium",
        "hazard_type": "rivers_risk",
        "type": "polygon"
    },
    "rivers_low": {
        "id": "flood_rivers_low", "label": "Rivers - Low Hazard",
        "file_path": "data/flood/FPM01_Risk_Rivers_Cardiff.geojson",
        "hazard_level": "low",
        "hazard_type": "rivers_risk",
        "type": "polygon"
    },
    "sea_high": {
        "id": "flood_sea_high", "label": "Sea - High Hazard",
        "file_path": "data/flood/FPM01_Risk_Sea_Cardiff.geojson",
        "hazard_level": "high",
        "hazard_type": "sea_risk",
        "type": "polygon"
    },
    "sea_medium": {
        "id": "flood_sea_medium", "label": "Sea - Medium Hazard",
        "file_path": "data/flood/FPM01_Risk_Sea_Cardiff.geojson",
        "hazard_level": "medium",
        "hazard_type": "sea_risk",
        "type": "polygon"
    },
    "sea_low": {
        "id": "flood_sea_low", "label": "Sea - Low Hazard",
        "file_path": "data/flood/FPM01_Risk_Sea_Cardiff.geojson",
        "hazard_level": "low",
        "hazard_type": "sea_risk",
        "type": "polygon"
    },
    "watercourses_high": {
        "id": "flood_watercourses_high", "label": "Surface Water - High Hazard",
        "file_path": "data/flood/FPM01_Risk_Watercourses_Cardiff.geojson",
        "hazard_level": "high",
        "hazard_type": "surface_risk",
        "type": "polygon"
    },
    "watercourses_medium": {
        "id": "flood_watercourses_medium", "label": "Surface Water - Medium Hazard",
        "file_path": "data/flood/FPM01_Risk_Watercourses_Cardiff.geojson",
        "hazard_level": "medium",
        "hazard_type": "surface_risk",
        "type": "polygon"
    },
    "watercourses_low": {
        "id": "flood_watercourses_low", "label": "Surface Water - Low Hazard",
        "file_path": "data/flood/FPM01_Risk_Watercourses_Cardiff.geojson",
        "hazard_level": "low",
        "hazard_type": "surface_risk",
        "type": "polygon"
    }
}

# Flood hazard colors mapped by type and level (consistent with BUILDING_COLOR_CONFIG)
FLOOD_HAZARD_COLORS = {
    "rivers_risk": {
        "high": [95, 158, 160, 255],
        "medium": [125, 180, 182, 255],
        "low": [160, 200, 202, 255]
    },
    "sea_risk": {
        "high": [30, 60, 140, 255],    
        "medium": [60, 100, 190, 255], 
        "low": [90, 140, 240, 255], 
    },
    "surface_risk": {
        "high": [28, 92, 120, 255],
        "medium": [75, 135, 165, 255],
        "low": [120, 180, 205, 255]
    }
}

# Configuration for dynamic building coloring
BUILDING_COLOR_CONFIG = {
    "none": { "label": "Default", "color": [220, 220, 220, 255] },
    "risk_rivers": { 
        "label": "Hazard from Rivers", 
        "column": "river_hazard", 
        "colors": { 
            "low": [160, 200, 202, 255], 
            "medium": [125, 180, 182, 255],
            "high": [95, 158, 160, 255]
        }
    },
    "risk_sea": { 
        "label": "Hazard from Sea", 
        "column": "sea_hazard", 
        "colors": { 
            "low": [90, 140, 240, 255], 
            "medium": [60, 100, 190, 255], 
            "high": [30, 60, 140, 255]    
        }
    },
    "risk_watercourses": { 
        "label": "Hazard from Surface Water", 
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
