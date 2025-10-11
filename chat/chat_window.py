# chat/chat_window.py

from dash import dcc, html

def create_chat_window():
    """
    Creates the layout for the chat window component.
    """
    initial_message_text = (
        "Welcome! | Croeso! I am Myrddin, and this is the DECIDE Decision Support System. I will be your AI Guide. Ask me a question or click on any layer in the bottom-left panel to learn more!. "
    )

    chat_window = html.Div(
        id="chat-window-container",
        className="chat-window-container",
        children=[
            html.Div(
                id="chat-history",
                className="chat-history",
                children=[
                    html.Div(
                        className="chat-message bot-message",
                        children=[
                            html.Img(src="assets/avatar.png", className="chat-avatar"),
                            html.Div(html.P(initial_message_text), className="chat-bot-content")
                        ]
                    )
                ],
                # --- NEW: Add a data attribute for the autoscroll callback to target ---
                **{'data-scroll-version': '0'}
            ),
            html.Div(
                className="chat-input-area",
                children=[
                    dcc.Input(
                        id="chat-input",
                        type="text",
                        placeholder="Ask a question...",
                        autoComplete="off",
                        n_submit=0,
                    ),
                    html.Button("Send", id="chat-send-btn", n_clicks=0)
                ]
            )
        ]
    )
    return chat_window

