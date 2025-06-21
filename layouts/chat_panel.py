"""
Chat panel layout for the Data Agent Platform application.
This file defines the layout for the chat interface.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

from constants import (
    CHAT_INPUT_ID, CHAT_MESSAGES_CONTAINER_ID, LOADING_INDICATOR_CONTAINER_ID, SEND_BUTTON_ID, SUGGESTION_AREA_ID
)

def create_chat_panel():
    """
    Create the chat panel layout.

    Returns:
        dbc.Col: The chat panel column with all its components.
    """
    return dbc.Col(className="chat-panel", width=6, children=[
        # Messages Area (Scrollable)
        dcc.Loading(
            id="loading-chat",
            type="default",
            children=html.Div(id=CHAT_MESSAGES_CONTAINER_ID, className="chat-container", children=[
                # Messages will be rendered here by callback
            ])
        ),

        # Suggestions Area
        html.Div(id=SUGGESTION_AREA_ID, className="suggestion-section", children=[
            # Suggestions will be rendered here by callback
        ]),

        # Loading Indicator Area
        html.Div(id=LOADING_INDICATOR_CONTAINER_ID, className='loading-indicator-container'),

        # Input Area (Fixed Bottom)
        create_chat_input_area()
    ])

def create_chat_input_area():
    """
    Create the chat input area with text input and send button.

    Returns:
        html.Div: The chat input area container.
    """
    return html.Div(className="chat-input-area", children=[
        dbc.Input(
            id=CHAT_INPUT_ID,
            placeholder="Ask about your data...", 
            type="text",
            className="chat-input",
            n_submit=0,  # Track number of Enter key presses
            autoComplete="off",  # Disable browser autocomplete
            debounce=True  # Debounce to prevent multiple submissions
        ),
        dbc.Button(
            html.I(className="fas fa-paper-plane"),
            id=SEND_BUTTON_ID,
            color="primary",
            className="send-button"
        )
    ])
