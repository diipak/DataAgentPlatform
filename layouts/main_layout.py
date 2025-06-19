import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def create_layout():
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("Dynamic Data Agent Platform", className="text-center mb-4")
            ], width=12)
        ]),

        # Global Error Alert Row
        dbc.Row([
            dbc.Col(
                dbc.Alert(
                    id="global-error-alert",
                    is_open=False,
                    dismissable=True,
                    duration=4000, # Optional: auto-dismiss after 4 seconds
                    color="danger"
                ),
                width=12 # Spans full width for visibility
            )
        ], className="mb-3"), # Add some margin below the alert

        # Dataset Selection Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Dataset Selection"),
                    dbc.CardBody([
                        html.Label("Select BigQuery Dataset:"),
                        dcc.Dropdown(
                            id='dataset-dropdown',
                            placeholder="Load datasets first...",
                            # Options will be populated by a callback
                        ),
                        dbc.Button("Load/Refresh Datasets", id="load-datasets-button", color="info", className="mt-2"),
                        dcc.Loading(
                            id="loading-datasets", # For feedback while loading datasets
                            type="default",
                            children=html.Div(id="dataset-load-status")
                        )
                        # Maybe a Div to show selected dataset details later: html.Div(id='selected-dataset-details')
                    ])
                ])
            ], width=12) # Or adjust width as needed
        ], className="mb-3"), # Add some margin
        
        # Main Content Row (Query Input & Results)
        dbc.Row([
            # Left Panel - Query Input
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Query Input"),
                    dbc.CardBody([
                        dbc.Textarea(
                            id="query-input",
                            placeholder="Enter your natural language query here...",
                            className="mb-3",
                            style={"height": "200px"}
                        ),
                        dbc.Button("Submit Query", id="submit-button", color="primary", className="me-1"), # Renamed
                        dbc.Button("Clear", id="clear-button", color="secondary") # Renamed
                    ])
                ])
            ], width=4),
            
            # Right Panel - Results
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Query Results & Visualizations"), # Updated Header
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-results",
                            children=[
                                html.H5("SQL Query:"),
                                dcc.Markdown(id="sql-query-display"), # To show the generated SQL
                                html.H5("Results Table:"),
                                html.Div(id="query-results-table"), # Renamed for the markdown table
                                html.H5("Visualizations:"),
                                html.Div(id="charts-display-area") # For dcc.Graph components
                            ],
                            type="default"
                        )
                    ])
                ])
            ], width=8)
        ]),
        
        # Insights Panel (already exists, should be fine)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Insights"), # This is for textual insights from VisualizationAgent
                    dbc.CardBody([
                        dcc.Loading( # Added loading for insights
                            id="loading-insights",
                            type="default",
                            children=[html.Div(id="insights-display-area")] # Renamed id for clarity
                        )
                    ])
                ])
            ], width=12)
        ], className="mt-3") # Added margin top for spacing
    ], fluid=True)
