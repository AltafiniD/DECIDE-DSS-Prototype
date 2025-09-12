# Decoding Cities for Informed Decision Making Decision Support System Prototype |DECIDE-DSS|

CC BY-NC-SA 4.0  
GNU GPL  

## Disclaimer ⚠️

This application is a prototype for demonstration and research purposes. Its code is not optimised for production, and some features may be incomplete or contain bugs. When loading the app for the first time, give it a moment as the datasets have to be loaded into memory. Additionally, when changing selections with larger datasets loaded (e.g., Buildings Analysis and Network Analysis), they may render the map unresponsive for a while as the data is reloaded. The application may occasionally crash; just reload your tab and the app should be responsive again.  

## Overview

https://github.com/user-attachments/assets/e28efc72-1557-4344-ad53-588b00ce2da5

Communication is a key aspect of decision support in urban studies, as we often interface with stakeholders with diverse backgrounds, agendas, and expertise. Models that support urban decisional processes must display actionable information, meaning being focused on accessibility, clarity, and sufficiency, rather than complexity, aiming to answer specific questions and inform outcomes.  

DECIDE-DSS is a prototype web-based application that follows the principles of universal design and outcome-driven decision-support strategies. It enables the visualisation of different layers of geospatial data and provides straightforward interpretation through essential KPIs and narrative functions. Its objective is to provide clear communication of the models' outcomes to diverse stakeholders. The demonstration of the prototype provides analysis of Cardiff, in the United Kingdom; however, it is flexible enough to be used in any urban context.  

The DSS aims to have two interchangeable versions:  
- A simple version, focused on communication and oriented to universal use.  
- An advanced/expert version, capable of natively performing more complex analysis and data processing, focused on urban analytics experts.  

## Features
- Interactive 3D map with customisable view modes.  
- Multi-Layer Data Visualisation: toggle and overlay various datasets, including:  
  - Road network  
  - Building footprints  
  - Neighbourhood boundaries  
  - Population density  
  - Land use  
  - Flood hazard zones  
    - Sea-bound hazard  
    - River-bound hazard  
    - Surface water and watercourses hazard  
  - Road network analysis  
  - Flood risk analysis  
    - Roads at risk  
    - Buildings at risk  
  - Antisocial Behaviour  
    - Crimes – Points and Hexmap  
    - Stop & Search – Points and Hexmap*  
- Data filtering functionality  
- Interactive Widgets Panel: dynamically updating graphs and KPIs that update based on selected data.  
- Custom Data Upload: user-uploaded GeoJSON files can be used within the app.  
- Customisable start screen and dashboard.*  
- Customisable chart and graphical options.*  
- Data sharing and report generator functionalities via a link or a PDF.*  
- Narrative AI Function*: provides the user with advice about the currently selected data and filter range. – Basic narrative function available.  
- Colour-coded "rating system" for performance metrics.*  
- Advanced analytics workspace for expert users.**  
- Scenario analysis & trends.**  
- Predictive modelling capabilities.**  
- Centralised data repository.**  

`*` indicates a feature partially implemented and/or to be fully implemented in the future.  
`**` indicates a feature to be implemented in the future advanced/expert version.  

### Tech Stack
- Backend & Frontend: [Dash](https://plotly.com/dash/) [Flask](https://flask.palletsprojects.com/en/stable/)  
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
├── data/        <- .geojson and .geoparquet demonstration data files should be placed here
│   └── flood/
├── layouts/
└── utils/
```
- `app.py`: Main entry point for the Dash application. Initialises the server and registers all callbacks.  
- `config.py`: Stores static configurations, such as Mapbox API keys, layer file paths, and map styles.  
- `/assets`: Contains static files like the main CSS stylesheet (style.css) and images for buttons.  
- `/callbacks`: Contains logic for the app’s interactivity.  
- `/chat`: Contains definitions for the chat window component.  
- `/components`: Reusable UI modules, such as widgets, control panels, and the filter panel.  
- `/data`: Contains the default GeoJSON and Geoparquet data files that the application loads on its first run.  
- `/layouts`: The `main_layout.py` file builds the overall HTML structure of the application.  
- `/utils`: A collection of helper functions for tasks like processing GeoJSON files.  

# Setup and Installation
To run this application locally, please follow these steps:  

1. Prerequisites:  
- `Python 3.12` or higher  
- A macOS or Windows machine (at least 16GB RAM recommended)  
- Safari or Firefox (Chrome and Edge not recommended)  
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
4. Install Package Dependencies in your terminal (Powershell - Windows | Terminal - MacOS | Bash/Terminal - Linux):
```
pip install -r requirements.txt
```
5. Mapbox API Key:

A Mapbox API Key is provided in the prototype, but in the event it expires, sign up for a free mapbox account [here](https://www.mapbox.com) and generate a new API Key. 
Copy your public access token (API Key) and paste it into line 4 of `config.py` here:
```
# Your Mapbox API key
MAPBOX_API_KEY = "<your key here>"
```
6. Add demonstration data
Download the data files from [Zenodo](https://zenodo.org/records/17105941), unzip them and place them into the Data folder
If different data files are added for testing, paths should be amended in config.py for each file respectively. 

7. Run the app in your terminal (Powershell - Windows | Terminal - MacOS | Bash/Terminal - Linux)
```
python3 app.py
```
Once the app is loaded, click or navigate to the IP address displayed in your terminal with your web browser to view the app. E.g. `http://127.0.0.1:8050`

## How to Use the Application
- Layers & Map Style: Use the control panel in the bottom-left to toggle data layers on and off and to change the base map style (Light, Dark, Satellite, Streets).
- Filtering Data: Click the handle at the bottom-center of the screen to slide up the filter panel. Adjust the sliders and dropdowns and click "Apply Filters" to update the data shown on the map. Clicking on segments within certain graphs (e.g., the Crime or Land Use charts) also acts as a filter and will update the map data automatically.
- Viewing Widgets: Click the handle on the right edge of the screen to open the widget slide-over panel containing detailed charts and statistics. These will update automatically as you apply filters.
- Click and drag to move around the map. Change zoom level by scrolling on a trackpad or mouse. To pan hold `Command ⌘` or `Ctrl` then click and drag. 
- Uploading Custom Data:
  - Click the "⚙️" icon in the bottom-left control panel to open the Settings modal.
  - Click "Upload File" next to the layer you wish to replace.
  - Select a valid GeoJSON file from your computer.
  - Custom data must use the `EPSG:4326 WGS 84` co-ordinate format. 
  - The server will automatically restart and load your new data for the current session. Your original data files in the /data directory will not be affected.

## Troubleshooting
- KeyError on startup: This usually means a GeoJSON file specified in `config.py` is missing a required property (e.g., a 'NAME' column for neighbourhoods). Ensure your custom data files have the same schema as the originals.
- Installation issues: If `pip install` fails, try creating a fresh virtual environment to resolve potential dependency conflicts.
- In-app uploads arent being recognised: Kill the server with `Control(⌃) + c` and rerun with `python3 app.py`.
- CSS sometimes does not apply correcly, leading to enlarged windows for the Narrative, Layers, Filters and KPIs windows. If this happens, please refresh the webapp to resolve.

## Future Developments

- Code Refactoring & Formatting: Review and refactor the entire codebase to improve organisation and ensure adherence to the best programming practices for long-term maintainability.
- Interactive Drawing & Area Selection Tools: Implement a feature allowing users to draw a custom shape or use a lasso tool on the map, instantly filtering all visible data to just that selected region.
- Enhanced Map-to-Widget Interactivity: Expand the map's click functionality so that selecting any data point, such as a specific crime or road segment, updates the side widgets with its detailed information.
- UI/UX Layout Refinement: Investigate alternative placements for the main filter panel, such as integrating it as a tab within the right-hand widget panel to declutter the main map view.
- URL-Based Sharing: Implement the share feature to generate a unique, sharable link that saves and reloads the user's complete session, including all filters and layer visibility.
- Production Server Deployment: Host the application on a production-grade server to ensure it is stable, secure, and capable of handling multiple simultaneous users as a real-world tool.
- AI-Enhanced Chatbot Functionality: Integrate true AI capabilities into the chatbot, allowing it to understand user queries, perform analysis, and proactively offer insights based on the data being viewed.
- Advanced Network Filter UI: Reorganise the single network analysis dropdown into multiple, logically grouped dropdowns (e.g., by 'Connectivity', 'Integration') to make the complex metrics easier to navigate.
- Live Data Integration: Transition key datasets from static files to live API or database connections, allowing the DSS to function as a real-time operational dashboard. 
- User Accounts & Personalisation: Implement a user login system where individuals can save their custom analysis zones, filter combinations, and preferred dashboard layouts between sessions.

## License

The DECIDE DSS prototype is set under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license (CC BY-NC-SA 4.0): you can, conditioned to giving appropriate credit to the authors, share, copy, redistribute and build upon the material. However you may not use the material for commercial purposes.

DECIDE DSS prototype is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. The GNU General Public License is intended to guarantee your freedom to share and change all versions of a program --to make sure it remains free software for all its users.

DECIDE DSS is distributed in the hope that it will be useful as a demonstrator and research tool, but WITHOUT ANY WARRANTY; without even the implied warranty of FITNESS FOR A PARTICULAR PURPOSE. See the CC BY-NC-SA 4.0 and GNU General Public License for more details.

You should have received a copy of both CC BY-NC-SA 4.0 and the GNU General Public License along with DECIDE DSS Prototype. If not, see https://creativecommons.org/licenses/by-nc-sa/4.0/ and http://www.gnu.org/licenses/.

## Funding

This research has received funding from the United Kingdom Research and Innova-tion Post Doctoral Fellowship Guarantee Scheme, set over the European Union’s Horizon Europe – Marie Skłodowska Curie Actions Post Doctoral Fellowships. UKRI Grant no. 101107846-DECIDE/EP/Y028716/1. Views and opinions expressed are those of the authors only, and do not necessarily reflect those of the United King-dom or European Union. Neither the United Kingdom or European Union nor the granting authority can be held responsible for them.











