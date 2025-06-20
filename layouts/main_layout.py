import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def create_layout():
    return dbc.Container([
        dcc.Store(id='store-generated-sql'), # Added dcc.Store here
        # Header
        dbc.Row([
            dbc.Col(html.H1("Dynamic Data Agent Platform", className="text-center mb-4"), width=12)
        ]),

        # Global Error Alert Row
        dbc.Row([
            dbc.Col(
                dbc.Alert(
                    id="global-error-alert",
                    is_open=False,
                    dismissable=True,
                    duration=4000,
                    color="danger"
                ),
                width=12
            )
        ], className="mb-3"),

        # Main Content Row
        dbc.Row([
            # Left Panel - Dataset Selection & Query Input
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Dataset & Query Input"), # Combined Header
                    dbc.CardBody([
                        html.Label("Select BigQuery Dataset:"),
                        dcc.Dropdown(
                            id='dataset-dropdown',
                            placeholder="Load datasets first...",
                        ),
                        dbc.Button("Load/Refresh Datasets", id="load-datasets-button", color="info", className="mt-2 mb-3"), # Added mb-3 for spacing
                        dcc.Loading(
                            id="loading-datasets",
                            type="default",
                            children=html.Div(id="dataset-load-status")
                        ),
                        html.Hr(), # Separator
                        html.Label("Enter your natural language query:"), # Clarifying label
                        dbc.Textarea(
                            id="query-input",
                            placeholder="e.g., 'What are the most common words in Shakespeare's works?'",
                            className="mb-3",
                            style={"height": "150px"} # Adjusted height
                        ),
                        dbc.Button("Submit Query", id="submit-button", color="primary", className="me-1"),
                        dbc.Button("Clear", id="clear-button", color="secondary")
                    ])
                ])
            ], width=4),
            
            # Right Panel - Query Results & Visualizations
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Query Results"), # Original Header
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-results",
                            type="default", # Ensure type is set
                            children=[
                                html.H5("Generated SQL Query:"), # More descriptive
                                dcc.Markdown(id="sql-query-display"),
                                html.Div([ # Wrapper for feedback elements
                                    dbc.Button(html.I(className="fas fa-thumbs-up"), id="sql-feedback-up-button", color="success", size="sm", className="me-1"),
                                    dbc.Button(html.I(className="fas fa-thumbs-down"), id="sql-feedback-down-button", color="danger", size="sm"),
                                    html.Div(id="sql-feedback-status", className="ms-2 d-inline-block", style={'fontSize': '0.9em'}) # For "Thanks" message
                                ], className="mt-2 mb-2"), # Add some margin
                                html.Hr(), # Separator before results table
                                html.H5("Query Results Data:"), # More descriptive
                                html.Div(id="query-results-table"),
                                html.Hr(), # Separator
                                html.H5("Visualizations:"),
                                html.Div(id="charts-display-area")
                            ]
                        )
                    ])
                ])
            ], width=8)
        ]),
        
        # Insights Panel
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Insights"),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-insights",
                            type="default",
                            children=[html.Div(id="insights-display-area")]
                        )
                    ])
                ])
            ], width=12)
        ], className="mt-3")
    ], fluid=True)
