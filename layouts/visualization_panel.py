"""
Visualization panel layout for the Data Agent Platform application.
This file defines the layout for the data visualization interface.
"""

from dash import html, dcc, callback_context, dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL

from constants import *

def create_data_source_configuration():
    """Creates the configuration section for the data source."""
    return html.Div(
        className="data-source-config",
        children=[
            # Hidden stores for dataset state management
            dcc.Store(id=SELECTED_DATASET_STORE, data=None),
            dcc.Store(id=DATASET_PROFILE_STORE, data=None),
            dbc.Label("BigQuery Table:", html_for=BIGQUERY_TABLE_INPUT_ID, className="config-label"),
            dbc.Input(
                id=BIGQUERY_TABLE_INPUT_ID,
                placeholder="project.dataset.table",
                type="text",
                value="bigquery-public-data.samples.shakespeare",  # Default value
                className="config-input"
            ),
            dbc.Button(
                "Browse Datasets",
                id="browse-datasets-btn",
                color="secondary",
                className="browse-datasets-btn",
                style={"marginTop": "0.5rem", "marginBottom": "0.5rem"}
            ),
            # Sidebar/modal for dataset selection
            dbc.Offcanvas(
                id=DATASET_SIDEBAR_ID,
                title="Browse BigQuery Datasets",
                is_open=False,
                placement="end",
                children=[
                    html.Div(id=DATASET_LIST_ID, children=[
                        html.P("Loading datasets...", style={"opacity": 0.7})
                    ])
                ],
                style={"width": "350px"}
            ),
            # Suggestion area for dataset-specific questions
            html.Div(
                id=SUGGESTION_AREA_ID,
                className="suggestion-area",
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "8px",
                    "marginTop": "1rem"
                }
            ),
            # Added by Cascade: Schema and Sample Data Display
            html.Div([
                dbc.Label("Schema:", className="config-label"),
                dcc.Textarea(id='schema-display', value='', readonly=True, className="schema-textarea")
            ], className="schema-section"), 
            html.Div([
                dbc.Label("Sample Data:", className="config-label"),
                html.Div(id='sample-data-display', className="sample-data-table")
            ], className="sample-data-section"), 
        ],
        style={"padding": "1rem 1.5rem", "border-bottom": "1px solid var(--border-color)"}
    )

def create_visualization_content():
    """Creates the main content area of the visualization panel, wrapped in a loading component."""
    return dcc.Loading(
        id="loading-visualization",
        type="default",
        children=html.Div(id=VISUALIZATION_CONTENT_AREA_ID, className="visualization-content", children=[
            # Content (Welcome message or results) will be rendered here by callback
            create_empty_state()
        ])
    )

def create_visualization_panel(metric_selector=None, app=None):
    """
    Create the visualization panel layout.
    
    Args:
        metric_selector: Optional metric selector component
        app: Dash app instance for registering callbacks
        
    Returns:
        dbc.Col: The visualization panel column
    """
    # Register callbacks if app is provided
    if app:
        register_callbacks(app)
        
    return dbc.Col(className="visualization-panel", width=6, children=[
        # Data Source Configuration
        create_data_source_configuration(),

        # Main content area (scrollable)
        create_visualization_content(),

        # Fixed Key Insights section at the bottom
        create_key_insights_section(metric_selector)
    ])

def create_empty_state():
    """
    Create the empty state display for when no data is available.

    Returns:
        html.Div: The empty state container.
    """
    return html.Div(className="empty-state-container", children=[
        html.Div("📊", style={"fontSize": "3rem", "marginBottom": "1rem"}),
        html.H3("Ask a question to see insights", className="subtitle"),
        html.P("Your query results and visualizations will appear here", style={"opacity": 0.7})
    ])

def create_key_insights_section(metric_selector=None):
    """
    Create the fixed key insights section at the bottom of the visualization panel.
    Enhanced with ADK to provide better visual separation and styling.

    Returns:
        html.Div: The key insights section container.
    """
    return html.Div(id=KEY_INSIGHTS_SECTION_ID, className="key-insights-fixed-section", children=[
        # Enhanced visual separator with gradient
        html.Div(className="key-insights-visual-separator"),

        # Title bar with icon
        html.Div(className="key-insights-title-bar", children=[
            html.Div(className="key-insights-title", children=[
                html.I(className="fas fa-lightbulb", style={"marginRight": "0.5rem"}),
                "Key Insights"
            ]),
            # Optional: Add a settings button for metric selection
            html.Div(className="key-insights-settings", children=[
                html.Div(id=KEY_INSIGHTS_METRIC_SELECTOR_ID, className="metric-selector", children=[
                    metric_selector.layout() if metric_selector else html.Div()
                ])
            ])
        ]),

        # Content area with scrollable design
        html.Div(id=KEY_INSIGHTS_CONTENT_ID, className="key-insights-content")
    ])

# Register callbacks for the visualization panel
def register_callbacks(app):
    """Register callbacks for the visualization panel."""
    # Toggle dataset sidebar
    @app.callback(
        Output(DATASET_SIDEBAR_ID, "is_open"),
        [Input("browse-datasets-btn", "n_clicks")],
        [State(DATASET_SIDEBAR_ID, "is_open")],
    )
    def toggle_offcanvas(n1, is_open):
        if n1:
            return not is_open
        return is_open
    
    # Load datasets into sidebar
    @app.callback(
        Output(DATASET_LIST_ID, "children"),
        [Input(DATASET_SIDEBAR_ID, "is_open")],
        prevent_initial_call=True
    )
    def load_datasets(is_open):
        if not is_open:
            return dash.no_update
            
        # Sample datasets - in a real app, this would query BigQuery
        datasets = [
            {"id": "bigquery-public-data.stackoverflow", "name": "Stack Overflow"},
            {"id": "bigquery-public-data.samples", "name": "Sample Datasets"},
            {"id": "bigquery-public-data.github_repos", "name": "GitHub Repos"},
            {"id": "bigquery-public-data.usa_names", "name": "USA Names"},
        ]
        
        return [
            dbc.ListGroup([
                dbc.ListGroupItem(
                    f"{ds['name']} ({ds['id']})",
                    id={"type": "dataset-select", "dataset": ds['id']},
                    action=True,
                    className="dataset-item"
                ) for ds in datasets
            ], flush=True)
        ]

    # Callback to highlight the selected dataset
    @app.callback(
        Output({"type": "dataset-select", "dataset": ALL}, "className"),
        Input(SELECTED_DATASET_STORE, "data"),
        State({"type": "dataset-select", "dataset": ALL}, "id"),
        prevent_initial_call=True
    )
    def highlight_selected_dataset(selected_dataset, all_dataset_ids):
        if not selected_dataset or not all_dataset_ids:
            return ["dataset-item"] * len(all_dataset_ids)

        class_names = []
        for dataset_id_obj in all_dataset_ids:
            current_dataset_id = dataset_id_obj.get('dataset')
            if current_dataset_id == selected_dataset:
                class_names.append("dataset-item active")
            else:
                class_names.append("dataset-item")
        
        return class_names
