# DECIDE Decision Support System Prototype

The DECIDE (Decoding Cities for Decision Making) DSS is a web based application enabling the analysis of geospatial data, designed for use in Cardiff and the surrounding South West reigon. 


## Features
- Interactive 3D Map
- Multi-Layer Data Visualization: Toggle and overlay various datasets, including: 
  - Neighbourhood Boundaries
  - Building Footprints
  - Crime Incidents (as points or a hexmap)
  - Population Density
  - Land Use
  - Road Network Analysis
  - Flood Risk Zones 
- Interactive Widgets Panel: Dynamically updating graphs and KPIs that update based on selected data. 
- Custom Data Upload: User uploaded GeoJSON files are able to be use within the app.
- Data sharing functionality via a link or a PDF.*
- Narrative AI Function*: Provides the user with advice about the currently selected data and filter range.*

`*`indicates a feature that is not fully implemented

### Tech Stack
- Backend & Frontend: [Dash](https://plotly.com/dash/)
- Mapping: [PyDeck](https://deckgl.readthedocs.io/en/latest/)
- Data Manipulation: [Pandas](https://pandas.pydata.org) & [Shapely](https://shapely.readthedocs.io/en/stable/)
- Charting: [Plotly Express](https://plotly.com/python/plotly-express/)

### Project Structure
```
├── app.py
├── config.py
├── assets/
│   └── images/
├── callbacks/
├── chat/
├── components/
├── data/        <- .geojson files should be placed here
│   └── flood/
├── layouts/
└── utils/
```
- `app.py`: Main entry point for the Dash application. Initializes the server and registers all callbacks.
- `config.py`: Stores static configurations, such as Mapbox API keys, layer file paths, and map styles.
- `/assets`: Contains static files like the main CSS stylesheet (style.css) and images for buttons.
- `/callbacks`: Contains logic for the apps interactivity.
- `/chat`: Contains definitions for the chat window component.
- `/components`: Reusable UI modules, such as widgets, control panels, and the filter panel.
- `/data`: Contains the default GeoJSON data files that the application loads on its first run.
- `/layouts`: The main_layout.py file builds the overall HTML structure of the application.
- `/utils`: A collection of helper functions for tasks like processing GeoJSON files.

## Disclaimer ⚠️

This application is a prototype. Its code is not optimized for production, and some features may be incomplete or contain bugs.
Loading the app for the first time will likely take a few minutes as the datasets have to be loaded into memory. Additionally, when changing selections with larger datasets loaded (e.g. Buildings) the map will be unresponsive for a while as the data is reloaded. The application may occasionally crash, just reload your tab and the app should be responsive again. 

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

5. Mapbox API Key:

Sign up for a free mapbox account [here](https://www.mapbox.com). Copy your public access token and paste it into line 4 of `config.py` here:
```
# Your Mapbox API key
MAPBOX_API_KEY = "<your key here>"
```

6. Add your data
Download the files from [here](https://www.google.com) and place them into the Data folder
Paths should be amended in config.py for each file respectively. 

7. Run the app
```
python3 app.py
```
Navigate to the IP address displayed in your terminal with your web browser to view the app. E.g. `http://127.0.0.1:8050`

## How to Use the Application
- Layers & Map Style: Use the control panel in the bottom-left to toggle data layers on and off and to change the base map style (Light, Dark, Satellite, Streets).
- Filtering Data: Click the handle at the bottom-center of the screen to slide up the filter panel. Adjust the sliders and dropdowns and click "Apply Filters" to update the data shown on the map. Clicking on segments within certain graphs (e.g., the Crime or Land Use charts) also acts as a filter and will update the map data automatically.
- Viewing Widgets: Click the handle on the right edge of the screen to open the widget slide-over panel containing detailed charts and statistics. These will update automatically as you apply filters.
- Uploading Custom Data:
  - Click the "⚙️" icon in the bottom-left control panel to open the Settings modal.
  - Click "Upload File" next to the layer you wish to replace.
  - Select a valid GeoJSON file from your computer.
  - The server will automatically restart and load your new data for the current session. Your original data files in the /data directory will not be affected.

## Troubleshooting
- KeyError on startup: This usually means a GeoJSON file specified in `config.py` is missing a required property (e.g., a 'NAME' column for neighbourhoods). Ensure your custom data files have the same schema as the originals.
- Installation issues: If `pip install` fails, try creating a fresh virtual environment to resolve potential dependency conflicts.
- In-app uploads arent being recognised: Kill the server with `Control(⌃) + c` and rerun with `python3 app.py`.





