# chat/chat_window.py

from dash import dcc, html

def create_chat_window():
    """
    Creates the layout for the chat window component.
    """
    initial_message_text = (
        "Croeso! | Welcome! This is the DECIDE Decision Support System. I am Myrddin, and I will be your AI Guide. Ask me a question or click on any layer in the bottom-left panel to learn more!."
    )

    # Create the chat history content (initial bot message only)
    chat_history = html.Div(
        id="chat-history",
        className="chat-history",
        children=[
            html.Div(
                className="chat-message bot-message",
                children=[
                    html.Div(html.P(initial_message_text), className="chat-bot-content")
                ]
            )
        ],
        # Data attribute for autoscroll callback
        **{'data-scroll-version': '0'}
    )

    # The chat container (keeps internal structure intact)
    chat_container = html.Div(
        id="chat-window-container",
        className="chat-window-container",
        children=[
            chat_history,
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

    # Wrapper that contains a persistent avatar toggle and the chat container.
    chat_wrapper = html.Div(
        id="chat-wrapper",
        className="chat-wrapper",
        children=[
            html.Button(html.Img(src="assets/avatar.png", className="chat-avatar"), id="toggle-chat-handle", n_clicks=0, className='chat-avatar-toggle'),
            chat_container
        ]
    )

    return chat_wrapper

