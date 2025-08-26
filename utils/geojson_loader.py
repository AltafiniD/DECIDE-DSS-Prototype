# utils/geojson_loader.py

import json
import pandas as pd
import requests

def process_geojson_features(file_path):
    """
    Loads a GeoJSON file and processes its features, correctly handling
    Polygons, MultiPolygons, Points, and LineStrings.
    Supports both local file paths and URLs.
    """
    try:
        if file_path.startswith("http://") or file_path.startswith("https://"):
            # Fetch the file content from the URL
            response = requests.get(file_path)
            response.raise_for_status()  # Raise an error for bad HTTP responses
            geojson_data = response.json()
        else:
            # Load the file from the local file system
            with open(file_path, 'r') as f:
                geojson_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, requests.RequestException) as e:
        print(f"Error loading {file_path}: {e}")
        return pd.DataFrame()

    features = geojson_data.get('features', [])
    if not features and isinstance(geojson_data, list):
        features = geojson_data

    processed_data = []
    for feature in features:
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})
        geom_type = geometry.get('type') if geometry else None
        
        if geom_type == 'MultiPolygon':
            for poly_coords in geometry.get('coordinates', []):
                contour = poly_coords[0]
                if contour and isinstance(contour, list) and len(contour) >= 3:
                    record = properties.copy()
                    record['contour'] = contour
                    processed_data.append(record)
        
        elif geom_type == 'Polygon':
            coords = geometry.get('coordinates')
            contour = coords[0] if coords else None
            if contour and isinstance(contour, list) and len(contour) >= 3:
                record = properties.copy()
                record['contour'] = contour
                processed_data.append(record)
        
        elif geom_type == 'Point':
            coords = geometry.get('coordinates')
            if coords and isinstance(coords, list) and len(coords) == 2:
                record = properties.copy()
                record['coordinates'] = coords
                processed_data.append(record)

        elif 'Longitude' in properties and 'Latitude' in properties:
            lon, lat = properties.get('Longitude'), properties.get('Latitude')
            if isinstance(lon, (int, float)) and isinstance(lat, (int, float)):
                record = properties.copy()
                record['coordinates'] = [lon, lat]
                processed_data.append(record)
        
        elif geom_type == 'LineString':
            coords = geometry.get('coordinates')
            if coords and isinstance(coords, list) and len(coords) >= 2:
                start_point, end_point = coords[0], coords[-1]
                if (isinstance(start_point, (list, tuple)) and len(start_point) >= 2 and
                    isinstance(end_point, (list, tuple)) and len(end_point) >= 2):
                    record = properties.copy()
                    record['source_position'], record['target_position'] = start_point, end_point
                    processed_data.append(record)

    if not processed_data:
        return pd.DataFrame()

    df = pd.DataFrame(processed_data)
    # Final check to ensure contour is valid before returning
    if 'contour' in df.columns:
        df = df[df['contour'].apply(lambda x: isinstance(x, list) and len(x) > 0)]

    df = df.replace({pd.NA: None})
    return df
