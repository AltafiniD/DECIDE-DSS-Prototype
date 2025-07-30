# utils/cache.py
import pandas as pd
from config import LAYER_CONFIG
from utils.geojson_loader import process_geojson_features

# Global cache dictionary to store loaded dataframes
DATA_CACHE = {}

def get_dataframe(layer_id):
    """
    Retrieves a DataFrame from the cache. If not present, it loads from
    the GeoJSON file specified in the config and stores it in the cache.
    """
    if layer_id not in DATA_CACHE:
        print(f"--- LAZY LOADING: Cache MISS for '{layer_id}'. Loading from file... ---")
        # Find the file path from the main configuration
        file_path = LAYER_CONFIG.get(layer_id, {}).get('file_path')
        if file_path:
            # Load the data using your existing processing function
            DATA_CACHE[layer_id] = process_geojson_features(file_path)
        else:
            # Store an empty DataFrame if no file path is found to prevent re-checks
            DATA_CACHE[layer_id] = pd.DataFrame()
            print(f"--- WARNING: No file_path found for layer_id '{layer_id}' in config. ---")
    
    # OPTIMIZATION: Return the direct reference from the cache.
    # We will no longer make a copy here to save memory.
    # The callbacks will be responsible for making copies if they need to mutate the data.
    return DATA_CACHE[layer_id]
