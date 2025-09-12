# callbacks/chat_callbacks.py

from dash.dependencies import Input, Output, State, ALL
from dash import html, no_update, ctx
from config import LAYER_CONFIG

# --- Data for interactive chat responses ---
LAYER_INFO = {
    "neighbourhoods": {
        "text": "This layer shows the 29 administrative community boundaries in Cardiff, which are the lowest tier of local government.",
        "questions": ["What is a community?", "How is this data useful?"]
    },
    "buildings": {
        "text": "This shows an integrated dataset of building footprints. You can color them by different flood risk types using the filter panel at the bottom.",
        "questions": ["Where does this data come from?" "What are the buildings at risk?"]
    },
    "flooding_toggle": {
        "text": "This toggles the flood hazard zones. Potential hazards from the sea, rivers, surface water and other watercourses can be visualised here. You can select which flood maps to combine and display in the filter panel.",
        "questions": ["Using the filters.", "What are the buildings at risk?", "What are the roads at risk?", "What do the different colors mean?" "Where does this data come from?"]
    },
    "network": {
        "text": "This layer displays the configurational analyses for the road-network. You can use the filters and the histograms to explore different analysis. Click in the buttons below to learn more about the analyses and significance of each measure.",
        "questions": ["What does configurational analysis mean?", "How do I use the histograms, what do they mean?", "How do I use the filters", "What is Integration (NAIN)", "What is Route Choice (NACH)?", "What is Kementrality (KBC)", "What is Degree Centrality (NADC)", "What are the Metric Measures (Rx)?", "What are Connectivity and Angular Connectivity" ]
    },
    "crime_master_toggle": {
        "text": "This toggles the crime data layers, related to antisocial behaviour in the city. You can view crimes as individual points or as a heatmap showing density. Use the sub-options to switch between views.",
        "questions": ["What's the difference between points and heatmap?", "Can I filter by crime type?"]
    },
    "deprivation": {
        "text": "This layer shows the Welsh Index of Multiple Deprivation (WIMD), indicating levels of household deprivation across different areas.",
        "questions": ["What is WIMD?", "What do the colors represent?"]
    },
    "land_use": {
        "text": "Displays the different types of land use across the city, such as residential, commercial, and green spaces, based on the UK's National Land Use database.",
        "questions": ["How can I filter by land use?", "Why is this important?"]
    },
    "population": {
        "text": "Visualizes population density data from the 2021 census for different Output Areas (OAs), the smallest geographical unit for census data.",
        "questions": ["What is an Output Area?", "How is density calculated?"]
    },
    "stop_and_search": {
        "text": "This layer shows locations of police Stop & Search events, related to control towards antisocial behaviour in the city. You can filter by the object of the search and by date range in the filter panel.",
        "questions": ["What does 'Object of search' mean?", "Where is this data from?"]
    }
}

PREDEFINED_ANSWERS = {
    # Neighbourhoods
    "What is a community?": "In Wales, a 'community' is the lowest tier of local government, similar to a civil parish in England, they are colloquially called neighbourhoods. Cardiff is divided into 29 of them.",
    "How is this data useful?": "Understanding community boundaries helps in analyzing demographic, social and envirionmental data at a very local level, which is useful for local governance and service planning.",
    # Buildings
    "Where does this data come from?": "This is an integrated dataset combining information from Ordnance Survey and other sources to provide a comprehensive view of building footprints, heights and morphology.",
    "What are the buildings at risk?": "By choosing a building risk type in the filter panel (Buildings at Risk), you can visualize which buildings are at risk from specific flood hazards.",
    # Flooding
    "Using the filters.": "Open the filter panel at the bottom of the screen. In Building & Environmental, you can select the flooding hazard layers and combine different hazard sources. You can also see the buildings at risk by selecting the drop down menu. In the newtork analysis tab, you can select the risk indexes that combine specific hazards with road-network performance metrics."
    "What are the buildings at risk?": "By choosing a building risk type in the filter panel (Buildings at Risk), you can visualize which buildings are at risk from specific flood hazards.",
    "What are the roads at risk?": "By choosing a risk index in the filter panel (Network Analysis), you can visualize which roads are at risk from specific flood hazards and what performance metric is affected.",
    "What do the different colors mean?": "Different colors represent different flood hazard types and their intensity and recurrence. Ligher colours indicate a higher recurrence interval, but a lower intensity, while darker colours indicate a lower recurrence interval, but a higher intensity.",
    "Where does this data come from?": "The flood hazard data is sourced from Natural Resources Wales (NRW), which provides detailed flood risk maps for various types of flooding in Wales.",
    # Network
    "What does configurational analysis mean?": "Configurational analysis is a way of studying a road network's layout to see how streets connect and how people and cars move around. This 'Space Syntax' helps us understand how easy it is to get to and through different areas, as well as how many different paths are available in the network. Essentially, it helps to make informed decisions about urban design by revealing both the strengths and weaknesses of the system.",
    "How do I use the histograms, what do they mean?": "The histograms show the distribution of values for the selected network measure, and let you examine the streets based on how important they are for accessibility, used as preferential routes or redundant for the system. Histograms are divided in 10 quartiles, with an equal count of streets to each, that show the data distribution. Clicking on a quartile will filter the streets that fall within that range, and showcase their hierarchical importance within this selection. This can be used to identify points of intervention or analyse the network structure.",
    "How do I use the filters": "You can use the filters in the bottom panel. In the section 'Network Analysis' you can select which measure to display. You can also select a range of values, that will be displayed on the histogram - the default visualization shows the whole network.",
    "What is Integration (NAIN)": "Integration (or Normalised Angular Integration - NAIN) is a global measure that informs how easily a street can be reached from all other streets in the network - or its relative accessibility. Streets with high integration values are more accessible and are often located in central areas, while streets with low integration values are less accessible and typically found in peripheral areas. This information is useful for urban analytics, as it identifies the roads that tend to attract more movement and activity.",
    "What is Route Choice (NACH)?": "Route Choice (or Normalised Angular Choice - NACH) is a global measure that informs how often a street is used as a preferential route through the system, considering the shortest path towards all other streets. Streets with high Choice values have a higher probability of being used as preferential routes. Streets with low Choice, tend to have a more local function, with less through movement. This information is useful for urban urban analytics as identifies the roads that tend to be used more often in the system",
    "What is Kementrality (KBC)": "Kementrality (or Kemeny-based Centrality - KBC) measures the overall redundancy of a street within the network. Streets with high Kementrality are less redundant, meaning they are more critical for maintaining the structure of the network. If removed, they may lead to significant changes in the system's accessibility. This information is useful for urban analytics as it helps to identify streets that are crucial for the network structure, as once removed, they may lead to a partial collapse in accessibility.",
    "What is Degree Centrality (NADC)": "Degree Centrality (or Normalised Angular Degree Centrality - NADC) is a global measure that informs the number of direct connections a street has to other streets in the network. Streets with high Degree Centrality are more connected and often serve as important junctions or hubs within the network. This information is useful for urban analytics as it helps to identify key streets that facilitate movement and connectivity within the area.",
    "What are the Metric Measures (Rx)?": "Metric measures restrict the global measures (NAIN, NACH and NADC) to a specific distance threshold in meters (i.e. 400m, 1200m, 2000m). This means that the calculations only consider streets within a defined radius from each street segment. This is useful for urban analytics, as it provides a more localized perspective of the network, highlighting the importance of streets within a distance that can be associated to pedestrian movement, cycling movement or local vehicular movement.",
    "What are Connectivity and Angular Connectivity": "Connectivity counts the number of direct connections a street has to other streets in the network, Angular Connectivity multiplies connectivity by the angle of the street. Streets that have a greater angle in between them have more impedance to movement when compared to streets with a lower angle, as individuals tend to prefer moving through areas that are more visible, so straighter. ",
    # Crime
    "What's the difference between points and heatmap?": "'Crime Points' shows the location of each individual crime event, which can be useful for seeing exact locations. The 'Crime Hexmap' aggregates these points into hexagonal bins to show the density and hotspots of crime more clearly.",
    "Can I filter by crime type?": "Yes. Open the filter panel and use the 'Crime Filters' dropdown to select one or more crime types you are interested in.",
    # Deprivation
    "What is WIMD?": "The Welsh Index of Multiple Deprivation (WIMD) is the official measure of relative deprivation for small areas in Wales. It combines various indicators like income, employment, health, and education.",
    "What do the colors represent?": "The map colors areas based on their deprivation percentile. Darker blue areas are more deprived compared to lighter areas, which are less deprived.",
    # Land Use
    "How can I filter by land use?": "In the filter panel, under 'Building & Environmental', you can use the 'Land Use Type' dropdown to select and view specific categories of land use.",
    "Why is this important?": "Analyzing land use helps planners and policymakers understand how the city is structured, identify areas for development, and ensure a balanced mix of residential, commercial, and recreational spaces.",
    # Population
    "What is an Output Area?": "Output Areas (OAs) are small geographical units created for census data. They are designed to have similar population sizes and be as socially homogenous as possible.",
    "How is density calculated?": "It's calculated as the number of usual residents in an Output Area divided by the area's size in hectares.",
    # Stop and Search
    "What does 'Object of search' mean?": "This refers to the reason the police conducted the stop and search. Common reasons include suspicion of carrying stolen goods, controlled drugs, or an offensive weapon.",
    "Where is this data from?": "This data is published by police forces in the UK as part of their commitment to transparency and is available through the data.police.uk portal."
}


def register_callbacks(app):
    """
    Registers all chat-related callbacks.
    """
    # Get the IDs for all non-crime layer toggles to build the State inputs
    other_layer_ids = [k for k, v in LAYER_CONFIG.items() if not k.startswith('crime_')]
    layer_toggle_states = [State(f"{layer_id}-toggle", "value") for layer_id in other_layer_ids]

    @app.callback(
        Output('chat-history', 'children'),
        Output('chat-input', 'value'),
        [Input('chat-send-btn', 'n_clicks'),
         Input('chat-input', 'n_submit'),
         Input({'type': 'layer-button', 'index': ALL}, 'n_clicks'),
         Input({'type': 'chat-question-btn', 'index': ALL}, 'n_clicks'),
         Input('crime-master-toggle-btn', 'n_clicks')],
        [State('chat-input', 'value'),
         State('chat-history', 'children'),
         State('crime-master-toggle', 'value'),  # State for the crime toggle
         *layer_toggle_states],  # Unpack all other layer states
        prevent_initial_call=True
    )
    def update_chat_history(send_clicks, enter_presses, layer_clicks, question_clicks, crime_toggle_click, user_input, chat_history, crime_toggle_state, *other_layer_states):
        triggered_id = ctx.triggered_id
        if not triggered_id:
            return no_update, no_update

        # --- Helper function to create a bot message ---
        def create_bot_message(text_content, questions=None):
            questions = questions or []
            question_buttons = []
            if questions:
                question_buttons = [html.Button(
                    q, 
                    id={'type': 'chat-question-btn', 'index': q}, 
                    className='chat-question-btn'
                ) for q in questions]

            message_content = html.Div(className="chat-bot-content", children=[
                html.P(text_content),
                html.Div(question_buttons, className='chat-question-buttons')
            ])

            return html.Div(className="chat-message bot-message", children=[
                html.Img(src="assets/avatar.png", className="chat-avatar"),
                message_content
            ])

        # --- Logic for Layer Button Clicks ---
        if isinstance(triggered_id, dict) and triggered_id.get('type') == 'layer-button':
            layer_id = triggered_id['index']
            
            try:
                # Find the state of the layer *before* the click
                layer_index = other_layer_ids.index(layer_id)
                current_state = other_layer_states[layer_index]
            except ValueError:
                return no_update, no_update
                
            # If state is empty, it means the layer was OFF and is now being turned ON
            if not current_state:
                if layer_id in LAYER_INFO:
                    info = LAYER_INFO[layer_id]
                    bot_response = create_bot_message(info['text'], info.get('questions'))
                    chat_history.append(bot_response)
                return chat_history, ""
            else:
                # Layer was ON and is being turned OFF, so do nothing
                return no_update, no_update

        # --- Logic for Crime Master Toggle ---
        if triggered_id == 'crime-master-toggle-btn':
            # Check the state of the crime toggle *before* the click
            if not crime_toggle_state:
                info = LAYER_INFO['crime_master_toggle']
                bot_response = create_bot_message(info['text'], info.get('questions'))
                chat_history.append(bot_response)
                return chat_history, ""
            else:
                # Crime toggle was ON and is being turned OFF, do nothing
                return no_update, no_update

        # --- Logic for Predefined Question Clicks ---
        if isinstance(triggered_id, dict) and triggered_id.get('type') == 'chat-question-btn':
            question_text = triggered_id['index']
            user_message = html.Div(className="chat-message user-message", children=html.P(question_text))
            chat_history.append(user_message)
            answer_text = PREDEFINED_ANSWERS.get(question_text, "I don't have an answer for that yet.")
            bot_response = create_bot_message(answer_text)
            chat_history.append(bot_response)
            return chat_history, ""

        # --- Logic for User Input (Send button or Enter) ---
        if (triggered_id == 'chat-send-btn' or triggered_id == 'chat-input') and user_input:
            user_message = html.Div(className="chat-message user-message", children=html.P(user_input))
            chat_history.append(user_message)
            bot_response = create_bot_message("I'm sorry, my AI features are not fully implemented yet. Please use the suggested questions.")
            chat_history.append(bot_response)
            return chat_history, ""

        return no_update, no_update
