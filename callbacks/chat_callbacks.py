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
        "questions": ["How do I color the buildings?", "Where does this data come from?"]
    },
    "flooding_toggle": {
        "text": "This toggles the visibility of flood risk zones from various sources, including the sea, rivers, and watercourses. You can select which flood maps to display in the filter panel.",
        "questions": ["What do the colors mean?", "Is my area at risk?"]
    },
    "network": {
        "text": "This layer displays the integrated road network. You can filter and color the roads by various network analysis metrics, like 'NAIN', which measures street-level integration.",
        "questions": ["What is NAIN?", "What is Connectivity?", "What is Choice?", "What is Integration?", "What is NACH?", "How do I filter the network?"]
    },
    "crime_master_toggle": {
        "text": "This toggles the crime data layers. You can view crimes as individual points or as a heatmap showing density. Use the sub-options to switch between views.",
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
        "text": "This layer shows locations of police Stop & Search events. You can filter by the object of the search and by date range in the filter panel.",
        "questions": ["What does 'Object of search' mean?", "Where is this data from?"]
    }
}

PREDEFINED_ANSWERS = {
    # Neighbourhoods
    "What is a community?": "In Wales, a 'community' is the lowest tier of local government, similar to a civil parish in England. Cardiff is divided into 29 of them.",
    "How is this data useful?": "Understanding community boundaries helps in analyzing demographic and social data at a very local level, which is useful for local governance and service planning.",
    # Buildings
    "How do I color the buildings?": "Open the filter panel at the bottom of the screen. Under 'Building & Environmental', use the 'Building Coloring' dropdown to select a flood risk type.",
    "Where does this data come from?": "This is an integrated dataset combining information from Ordnance Survey and other sources to provide a comprehensive view of building footprints.",
    # Flooding
    "What do the colors mean?": "The different shades represent different sources of potential flooding, like from the sea or from rivers. You can turn them on and off in the filter panel to see the specific zones.",
    "Is my area at risk?": "By turning on the flood layers and the building layer, you can visually inspect which buildings fall within the flood risk zones. The 'Buildings at Risk' widget on the right panel also gives a total count.",
    # Network
    "What is NAIN?": "NAIN (Normalised Angular Integration) is a metric from space syntax analysis. Higher values (typically shown in warmer colors) indicate streets that are more integrated and accessible within the network, often corresponding to main routes.",
    "How do I filter the network?": "In the filter panel, under 'Network Analysis', you can select a metric from the dropdown and then use the slider to filter the road segments based on their metric values.",
    "What is Connectivity?": "Connectivity is the simplest metric. It's a direct count of how many other street segments are immediately connected to a specific segment. It tells you how many turning options you have at that point.",
    "What is Choice?": "'Choice' (or T1024_Choice) measures 'through-movement' potential. It counts how many of the simplest paths between all pairs of streets in the network pass through a specific street. Streets with high Choice are the main arteries and thoroughfares of the city.",
    "What is Integration?": "'Integration' (T1024_Integration) measures how close a street is to all others, based on the fewest turns. High integration streets are easily reachable from everywhere and often form the core of a community or a city's activity centers.",
    "What is NACH?": "NACH (Normalised Angular Choice) also measures 'through-traffic' potential, like Choice. High NACH values highlight streets that are crucial for connecting different parts of the network with the simplest routes (fewest turns).",
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

