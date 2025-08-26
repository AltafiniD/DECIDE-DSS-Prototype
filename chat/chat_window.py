# chat/chat_window.py

from dash import dcc, html

def create_chat_window():
    """
    Creates the layout for the chat window component.
    """
    # --- MODIFIED: Only the first message is now created initially ---
    initial_message_text = (
        "Here is the narrative window. This is an AI assistant that will eventually display "
        "dynamic information based on what's currently selected, helping you to make informed decisions."
    )

    chat_window = html.Div(
        id="chat-window-container",
        className="chat-window-container",
        children=[
            # Div to hold the chat history
            html.Div(
                id="chat-history",
                className="chat-history",
                children=[
                    # The initial message
                    html.Div(
                        className="chat-message bot-message",
                        children=[
                            html.Img(src="https://placehold.co/40x40/333333/EFEFEF?text=Bot", className="chat-avatar"),
                            html.P(initial_message_text)
                        ]
                    )
                ]
            ),
            # Div for the user input area
            html.Div(
                className="chat-input-area",
                children=[
                    dcc.Input(
                        id="chat-input",
                        type="text",
                        # --- MODIFIED: Placeholder text is updated for interactivity ---
                        placeholder="Type anything to continue...",
                        autoComplete="off",
                        n_submit=0,
                    ),
                    html.Button("Send", id="chat-send-btn", n_clicks=0)
                ]
            )
        ]
    )
    return chat_window
