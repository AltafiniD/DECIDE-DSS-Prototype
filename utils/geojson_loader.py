# utils/geojson_loader.py

import json
import pandas as pd
import numpy as np

def process_geojson_features(file_path):
    """
    Loads a GeoJSON file and processes its features, intelligently handling
    polygons, points (from Longitude/Latitude), and linestrings.
    """
    try:
        with open(file_path, 'r') as f:
            geojson_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return pd.DataFrame()

    features = geojson_data.get('features', [])
    if not features and isinstance(geojson_data, list):
        features = geojson_data

    processed_data = []
    for feature in features:
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})

        if geometry and geometry.get('type') in ['Polygon', 'MultiPolygon']:
            coords = geometry.get('coordinates')
            contour = None
            if geometry.get('type') == 'Polygon' and coords:
                contour = coords[0]
            elif geometry.get('type') == 'MultiPolygon' and coords and coords[0]:
                contour = coords[0][0]

            if contour and isinstance(contour, list) and len(contour) >= 3:
                is_valid = all(
                    isinstance(p, (list, tuple)) and len(p) >= 2 and
                    isinstance(p[0], (int, float)) and isinstance(p[1], (int, float))
                    for p in contour
                )
                if is_valid:
                    record = properties.copy()
                    record['contour'] = contour
                    processed_data.append(record)
        elif 'Longitude' in properties and 'Latitude' in properties:
            lon, lat = properties.get('Longitude'), properties.get('Latitude')
            if isinstance(lon, (int, float)) and isinstance(lat, (int, float)):
                record = properties.copy()
                record['coordinates'] = [lon, lat]
                processed_data.append(record)
        elif geometry and geometry.get('type') == 'LineString':
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
    df = df.replace({np.nan: None})
    return df
