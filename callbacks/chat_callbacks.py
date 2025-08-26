# callbacks/chat_callbacks.py

from dash.dependencies import Input, Output, State
from dash import html, no_update, ctx

# --- NEW: Define the tutorial messages here ---
TUTORIAL_MESSAGES = [
    (
        "To get started, you can explore the different data layers. Use the panel in the "
        "bottom-left to toggle layers like buildings, crime, and population, and to change the map style."
    ),
    (
        "At the bottom of the screen, you'll find the filter panel. You can slide it up to filter the "
        "data by time, crime type, network metrics, and more. Click 'Apply Filters' to see your changes."
    ),
    (
        "Finally, the panel on the right contains detailed widgets and graphs. Click the tab to open it. "
        "These visualizations will update automatically as you filter and select data on the map."
    ),
    (
        "You're all set! Feel free to explore the data. This chat window will have more AI features soon."
    )
]

def register_callbacks(app):
    """
    Registers all chat-related callbacks.
    """
    @app.callback(
        Output('chat-history', 'children'),
        Output('chat-input', 'value'),
        Output('chat-input', 'placeholder'), # --- NEW: Added placeholder output
        Input('chat-send-btn', 'n_clicks'),
        Input('chat-input', 'n_submit'),
        State('chat-input', 'value'),
        State('chat-history', 'children'),
        prevent_initial_call=True
    )
    def update_chat_history(send_clicks, enter_presses, user_input, chat_history):
        triggered_id = ctx.triggered_id
        placeholder_text = "Type anything to continue..."

        if not triggered_id or not user_input:
            return no_update, no_update, no_update

        # Add the user's message
        user_message = html.Div(className="chat-message user-message", children=html.P(user_input))
        updated_history = chat_history + [user_message]

        # Count existing bot messages to determine the next tutorial step
        bot_message_count = sum(1 for item in chat_history if isinstance(item, dict) and 'bot-message' in item.get('props', {}).get('className', ''))
        
        # The next message index is the number of bot messages already sent minus one
        next_message_index = bot_message_count - 1

        if 0 <= next_message_index < len(TUTORIAL_MESSAGES):
            bot_response_text = TUTORIAL_MESSAGES[next_message_index]
            if next_message_index == len(TUTORIAL_MESSAGES) - 1:
                placeholder_text = "Ask about the data..." # Final placeholder
        else:
            # Default response after the tutorial is over
            bot_response_text = "I'm sorry, my AI features are not fully implemented yet."
            placeholder_text = "Ask about the data..."

        bot_response = html.Div(
            className="chat-message bot-message",
            children=[
                html.Img(src="https://placehold.co/40x40/333333/EFEFEF?text=Bot", className="chat-avatar"),
                html.P(bot_response_text)
            ]
        )

        updated_history.append(bot_response)

        return updated_history, "", placeholder_text
