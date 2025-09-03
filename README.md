# DECIDE Decision Support System Prototype

The DECIDE (Decoding Cities for Decision Making) DSS is a web based application enabling the analysis of geospatial data, designed for use in Cardiff and the surrounding South West reigon. 


## Features
- Interactive 3D Map: Utilizes pydeck and Mapbox to render an extruded 3D map of the city, providing a rich and immersive user experience.
- Multi-Layer Data Visualization: Toggle and overlay various datasets, including:
-- Neighbourhood Boundaries
-- Building Footprints
-- Crime Incidents (as points or a hexmap)
-- Population Density
-- Land Use
-- Road Network Analysis
-- Flood Risk Zones 
- Interactive Widgets Panel: Dynamically updating graphs and KPIs that update based on selected data. 
- Custom Data Upload: User uploaded GeoJSON files are able to be use within the app.
- Data sharing functionality via a link or a PDF.*
- Narrative AI Function*: Provides the user with advice about their current selection...

`*`indicates a feature that is not fully implemented

### Tech Stack
Backend & Frontend: [Dash](https://plotly.com/dash/)
Mapping: [PyDeck](https://deckgl.readthedocs.io/en/latest/)
Data Manipulation: [Pandas](https://pandas.pydata.org) & [Shapely](https://shapely.readthedocs.io/en/stable/)
Charting: [Plotly Express](https://plotly.com/python/plotly-express/)

### Project Structure
```
├── app.py #main entrypoint of the app
├── config.py
├── assets/
│   └── images/ #icon images etc
├── callbacks/
├── chat/
├── components/
├── data/ #.geojson files should be placed here
│   └── flood/
├── layouts/
└── utils/
```
--app.py: Main entry point for the Dash application. Initializes the server and registers all callbacks.
--config.py: Stores all static configurations, such as Mapbox API keys, layer file paths, and map styles.
--/assets: Contains static files like the main CSS stylesheet (style.css) and images for buttons.
--/callbacks: The engine of the app. Each file contains the logic for a specific part of the application's interactivity.
--/chat: Contains the UI definition for the chat window component.
--/components: Reusable UI modules, such as widgets, control panels, and the filter panel.
--/data: Contains the default GeoJSON data files that the application loads on its first run.
--/layouts: The main_layout.py file builds the overall HTML structure of the application.
--/utils: A collection of helper functions for tasks like processing GeoJSON files and defining color schemes.

# Setup and Installation
To run this application locally, please follow these steps:
1. Prerequisites:
- `Python 3.12` or higher
- A macOS or Windows machine (at least 16GB RAM reccomended)
- `pip` package installer

2. Clone the Repository:
```
cd <your repo folder>
git clone https://github.com/AltafiniD/DECIDE---Decision-Support-System-Prototype
```

3. Create a Virtual Environment (Optional)
```
python3 -m venv venv
# macOS: source venv/bin/activate  
# Windows: venv\Scripts\activate
```

4. Install Package Dependencies:
```
pip install -r requirements.txt
```

5. Mapbox API Key
Sign up for a free mapbox account [here](https://www.mapbox.com). Copy your public access token and paste it into line 4 of `config.py` here:
```
# Your Mapbox API key
MAPBOX_API_KEY = "<your key here>"
```

6. Add your data
Files can be found here.. or supply your own.
Paths should be amended in config.py for each file respectively. 

7. Run the app
```
python3 app.py
```
Navigate to the IP address displayed in your terminal with your web browser to view the app. E.g. `http://127.0.0.1:8050`

# How to Use the Application
- Layers & Map Style: Use the control panel in the bottom-left to toggle data layers on and off and to change the base map style (Light, Dark, Satellite, Streets).
- Filtering Data: Click the handle at the bottom-center of the screen to slide up the filter panel. Adjust the sliders and dropdowns and click "Apply Filters" to update the data shown on the map.
- Viewing Widgets: Click the handle on the right edge of the screen to open the slide-over panel containing detailed charts and statistics. These will update automatically as you apply filters.
- Uploading Custom Data:
-- Click the "⚙️" icon in the bottom-left control panel to open the Settings modal.
-- Click "Upload File" next to the layer you wish to replace.
-- Select a valid GeoJSON file from your computer.
-- The server will automatically restart and load your new data for the current session. Your original data files in the /data directory will not be affected.


