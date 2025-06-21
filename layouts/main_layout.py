import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from layouts.chat_panel import create_chat_panel
from layouts.visualization_panel import create_visualization_panel

def create_layout():
    return html.Div(className="app-container dark-theme", children=[
        # Store components
        dcc.Store(id='store-generated-sql'),
        dcc.Store(id='store-chat-messages', data=[]),
        dcc.Store(id='store-current-data', data={}),
        
        # Two-panel layout
        html.Div(className="main-panels", children=[
            # Left Panel - Chat Interface
            html.Div(className="chat-section", children=[
                # Chat Header
                html.Div(className="chat-header", children=[
                    html.Div(className="chat-title-container", children=[
                        html.I(className="fas fa-robot chat-icon"),
                        html.Div(children=[
                            html.H2("Data Agent Chatbot", className="chat-title"),
                            html.P("Ask questions about your data", className="chat-subtitle")
                        ])
                    ])
                ]),
                
                # Chat Messages Area
                html.Div(className="chat-messages-container", children=[
                    # Welcome message
                    html.Div(className="welcome-message", children=[
                        "Welcome to the Data Agent Platform! Ask me anything about your data."
                    ]),
                    
                    # Chat messages will be added here dynamically
                    html.Div(id="chat-messages", className="chat-messages"),
                ]),
                
                # Suggested Questions
                html.Div(className="suggestions-container", children=[
                    html.P("Suggested Questions:", className="suggestions-title"),
                    html.Div(className="suggestion-buttons", children=[
                        dbc.Button("What is the total number of records in this dataset?", 
                                 id="suggestion-1", className="suggestion-btn", color="outline-light", size="sm"),
                        dbc.Button("Show me the first 10 rows of data", 
                                 id="suggestion-2", className="suggestion-btn", color="outline-light", size="sm"),
                        dbc.Button("What columns are available in this dataset?", 
                                 id="suggestion-3", className="suggestion-btn", color="outline-light", size="sm"),
                        dbc.Button("Show me a summary of the data", 
                                 id="suggestion-4", className="suggestion-btn", color="outline-light", size="sm"),
                    ])
                ]),
                
                # Chat Input Area
                html.Div(className="chat-input-container", children=[
                    dbc.InputGroup(children=[
                        dbc.Input(
                            id="chat-input",
                            placeholder="Type your message...",
                            className="chat-input"
                        ),
                        dbc.Button(
                            html.I(className="fas fa-paper-plane"),
                            id="send-button",
                            color="primary",
                            className="send-button"
                        )
                    ])
                ])
            ]),
            
            # Right Panel - Data Insights
            html.Div(className="insights-section", children=[
                # Insights Header
                html.Div(className="insights-header", children=[
                    html.Div(className="insights-title-container", children=[
                        html.H2("Data Insights", className="insights-title"),
                        html.P("Visualizations and analysis from your queries", className="insights-subtitle")
                    ]),
                    # Theme toggle button
                    dbc.Button(
                        html.I(className="fas fa-moon"),
                        id="theme-toggle",
                        color="outline-light",
                        size="sm",
                        className="theme-toggle"
                    )
                ]),
                
                # Dataset Selection
                html.Div(className="dataset-selection-container", children=[
                    html.Label("Select BigQuery Dataset", className="dataset-label"),
                    html.Div(className="d-flex align-items-center gap-2", children=[
                        dcc.Dropdown(
                            id='dataset-dropdown-visible',
                            placeholder="Select a dataset...",
                            className="flex-grow-1",
                            style={"minWidth": "300px"}
                        ),
                        dbc.Button(
                            html.I(className="fas fa-sync-alt"),
                            id="load-datasets-button-visible",
                            color="outline-secondary",
                            size="sm"
                        )
                    ]),
                    dcc.Loading(
                        id="loading-datasets-visible",
                        type="default",
                        children=html.Div(id="dataset-load-status-visible", className="mt-2 dataset-load-status")
                    ),
                ]),
                
                # Main Visualization Area
                html.Div(className="visualization-area", children=[
                    dcc.Loading(
                        id="loading-visualization",
                        type="default",
                        children=html.Div(id="main-visualization", className="main-chart")
                    )
                ]),
                
                # Data Table Section
                html.Div(className="data-table-section", children=[
                    html.H3("Data Table", className="section-title"),
                    dcc.Loading(
                        id="loading-table",
                        type="default",
                        children=html.Div(id="data-table", className="data-table-container")
                    )
                ]),
                
                # Key Insights Section
                html.Div(className="key-insights-section", children=[
                    html.Div(className="key-insights-header", children=[
                        html.I(className="fas fa-lightbulb insight-icon"),
                        html.H3("Key Insights", className="section-title")
                    ]),
                    html.Div(id="key-insights", className="insights-list")
                ])
            ])
        ]),
        
        # Hidden elements for compatibility
        html.Div(style={"display": "none"}, children=[
            dcc.Dropdown(id='dataset-dropdown'),
            dbc.Button(id="load-datasets-button"),
            html.Div(id="dataset-load-status"),
            dbc.Textarea(id="query-input"),
            dbc.Button(id="submit-button"),
            dbc.Button(id="clear-button"),
            html.Div(id="sql-query-display"),
            html.Div(id="query-results-table"),
            html.Div(id="charts-display-area"),
            html.Div(id="insights-display-area"),
            dbc.Button(id="sql-feedback-up-button"),
            dbc.Button(id="sql-feedback-down-button"),
            html.Span(id="sql-feedback-status"),
            dbc.Alert(id="global-error-alert", is_open=False)
        ])
    ])
