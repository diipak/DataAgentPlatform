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
        
        # Main Content
        dbc.Row([
            # Left Panel - Query Input
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Query Input"),
                    dbc.CardBody([
                        dbc.Textarea(
                            id="query-input",
                            placeholder="Enter your query here...",
                            className="mb-3",
                            style={"height": "200px"}
                        ),
                        dbc.Button("Submit Query", id="submit-query", color="primary", className="me-1"),
                        dbc.Button("Clear", id="clear-query", color="secondary")
                    ])
                ])
            ], width=4),
            
            # Right Panel - Results
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Query Results"),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-results",
                            children=[
                                html.Div(id="query-results")
                            ],
                            type="default"
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
                        html.Div(id="insights")
                    ])
                ])
            ], width=12)
        ])
    ], fluid=True)
