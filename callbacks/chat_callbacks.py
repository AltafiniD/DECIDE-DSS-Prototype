# callbacks/chat/chat_callbacks.py

from dash.dependencies import Input, Output, State
from dash import html, no_update, ctx

def register_callbacks(app):
    """
    Registers all chat-related callbacks.
    """
    @app.callback(
        Output('chat-history', 'children'),
        Output('chat-input', 'value'),
        Input('chat-send-btn', 'n_clicks'),
        Input('chat-input', 'n_submit'), # Trigger on Enter key
        State('chat-input', 'value'),
        State('chat-history', 'children'),
        prevent_initial_call=True
    )
    def update_chat_history(send_clicks, enter_presses, user_input, chat_history):
        triggered_id = ctx.triggered_id

        if not triggered_id or not user_input:
            return no_update, no_update

        # --- MODIFIED: User message text is now wrapped in a <p> tag ---
        user_message = html.Div(className="chat-message user-message", children=html.P(user_input))
        
        # --- MODIFIED: Bot response now includes the avatar image and a <p> tag ---
        bot_response_text = "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
        bot_response = html.Div(
            className="chat-message bot-message",
            children=[
                html.Img(src="https://placehold.co/40x40/333333/EFEFEF?text=Bot", className="chat-avatar"),
                html.P(bot_response_text)
            ]
        )

        updated_history = chat_history + [user_message, bot_response]

        return updated_history, ""
