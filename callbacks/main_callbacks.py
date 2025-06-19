import os
import json
import logging
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Import Agents
from agents import SchemaAgent, DataAnalystAgent, VisualizationAgent

# Configure logging
logger = logging.getLogger(__name__)

# Agent Initialization
# Ideally, project_id is fetched once and agents are initialized once.
# For simplicity in this subtask, we might re-initialize or fetch project_id in callbacks,
# but a better pattern is to initialize them in app.py or a central place.

# Placeholder for project_id - this should be robustly fetched
try:
    PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")

    # Initialize agents here if they are stateless or if their state is managed per request.
    # For this iteration, let's assume they can be initialized once if their internal state
    # doesn't conflict between requests. BigQueryConnector within agents might need care
    # if not thread-safe or if it holds per-request state.
    # However, ADK agents are generally designed to be instantiated.
    # Let's instantiate them per call for safety in a web context for now,
    # or ensure their methods are re-entrant.
    # For this subtask, we will instantiate them within the callback.

except KeyError:
    logger.error("CRITICAL: GOOGLE_CLOUD_PROJECT environment variable is not set.")
    PROJECT_ID = None # App will likely be non-functional

def register_callbacks(app):

    @app.callback(
        [Output('dataset-dropdown', 'options'),
         Output('dataset-dropdown', 'value'),
         Output('dataset-load-status', 'children')],
        [Input('load-datasets-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def load_datasets(n_clicks):
        if not n_clicks:
            raise PreventUpdate

        if not PROJECT_ID:
            return [], None, "Error: GOOGLE_CLOUD_PROJECT not configured."

        try:
            logger.info("Instantiating SchemaAgent to load datasets.")
            schema_agent = SchemaAgent(project_id=PROJECT_ID)
            if not schema_agent.connector: # Check if connector initialized successfully
                 return [], None, "Error: SchemaAgent failed to connect to BigQuery."

            datasets = schema_agent.get_available_datasets()
            if not datasets:
                return [], None, "No datasets found or error fetching them."

            options = [{'label': ds_id, 'value': ds_id} for ds_id in datasets]
            logger.info(f"Loaded {len(datasets)} datasets for dropdown.")
            # Select the first dataset by default, or None if empty
            default_value = options[0]['value'] if options else None
            return options, default_value, f"Successfully loaded {len(datasets)} datasets."
        except Exception as e:
            logger.error(f"Error loading datasets: {e}", exc_info=True)
            return [], None, f"Error loading datasets: {str(e)}"

    @app.callback(
        [Output('sql-query-display', 'children'),
         Output('query-results-table', 'children'),
         Output('charts-display-area', 'children'),
         Output('insights-display-area', 'children'),
         Output('query-input', 'value', allow_duplicate=True)], # allow_duplicate to clear input
        [Input('submit-button', 'n_clicks')],
        [State('query-input', 'value'),
         State('dataset-dropdown', 'value')],
        prevent_initial_call=True
    )
    def handle_query_submission(n_clicks, query_text, selected_dataset):
        if not n_clicks:
            raise PreventUpdate

        if not PROJECT_ID:
            return "Error: GCP Project not configured.", "", [], "", query_text
        
        if not query_text:
            return "Error: Query cannot be empty.", "", [], "", query_text

        if not selected_dataset:
            return "Error: Please select a dataset first.", "", [], "", query_text

        logger.info(f"Handling query: '{query_text}' for dataset: '{selected_dataset}'")

        try:
            # 1. Initialize Agents
            logger.info("Initializing agents for query processing.")
            # These agents now correctly use project_id for their connectors as per previous subtasks
            schema_agent = SchemaAgent(project_id=PROJECT_ID)
            data_analyst_agent = DataAnalystAgent() # DataAnalystAgent __init__ handles project_id internally
            visualization_agent = VisualizationAgent()

            if not schema_agent.connector or not data_analyst_agent.connector:
                 # Error messages for specific agent failures
                error_msg = "Error: Agent(s) failed to connect to BigQuery. Check logs."
                # Check which specific agent failed if possible
                if not schema_agent.connector:
                    logger.error("SchemaAgent connector failed to initialize.")
                if not data_analyst_agent.connector: # Assuming DataAnalystAgent has a 'connector' attribute after init
                    logger.error("DataAnalystAgent connector failed to initialize.")
                return error_msg, "", [], "", query_text

            # 2. Get Full Dataset Schema
            logger.info(f"Fetching full schema for dataset: {selected_dataset}")
            full_schema = schema_agent.get_full_dataset_schema(selected_dataset)

            # Check if full_schema itself is empty or if any table within it has an error
            if not full_schema or any(table_info.get('error') for table_name, table_info in full_schema.items() if isinstance(table_info, dict)):
                logger.error(f"Failed to retrieve full schema for {selected_dataset} or schema contains errors.")
                schema_errors = {k: v.get('error') for k,v in full_schema.items() if isinstance(k, dict) and v.get('error')} if full_schema else {}
                error_detail = f" Could not retrieve schema for some tables: {schema_errors}" if schema_errors else " Schema might be empty or inaccessible."
                return f"Error: Failed to get complete schema for dataset {selected_dataset}.{error_detail}", "", [], "", query_text

            # 3. Process with DataAnalystAgent
            logger.info("Processing query with DataAnalystAgent.")
            analysis_result = data_analyst_agent.process(
                query=query_text,
                dataset_schema=full_schema,
                project_id=PROJECT_ID, # project_id is now explicitly passed to process
                dataset_id=selected_dataset
            )

            if analysis_result.get('error'):
                logger.error(f"DataAnalystAgent error: {analysis_result['error']}")
                # Display SQL query if available even if execution failed
                sql_display_content = f"```sql\n{analysis_result.get('sql_query', 'N/A')}\n```" if analysis_result.get('sql_query') else "No SQL query generated."
                sql_display = dcc.Markdown(sql_display_content)
                return sql_display, f"Error during data analysis: {analysis_result['error']}", [], "", query_text

            sql_query_md = dcc.Markdown(f"```sql\n{analysis_result['sql_query']}\n```")

            # Ensure results_markdown from DataAnalystAgent is directly usable or wrap in dcc.Markdown
            results_content = analysis_result.get('results_markdown', "No tabular results to display.")
            results_md_component = dcc.Markdown(results_content) if isinstance(results_content, str) else results_content

            # 4. Generate Visualizations
            charts_components = []
            insights_text_combined = ""
            if analysis_result.get('results_df') is not None and not analysis_result['results_df'].empty:
                logger.info("Generating visualizations with VisualizationAgent.")
                viz_result = visualization_agent.generate_visualizations(
                    data_df=analysis_result['results_df'],
                    query=query_text
                )

                # Prepare chart components
                for chart_json_str in viz_result.get('charts', []):
                    try:
                        chart_fig = json.loads(chart_json_str)
                        charts_components.append(dcc.Graph(figure=chart_fig))
                    except Exception as e:
                        logger.error(f"Error loading chart JSON: {e}", exc_info=True)
                        charts_components.append(html.Pre(f"Error loading chart: {str(e)}"))

                insights_text_combined = viz_result.get('insights_text', "")
            else:
                insights_text_combined = "Query returned no data or an error occurred, so no visualizations were generated."
                logger.info("No data for visualization or DataAnalystAgent returned empty/None DataFrame.")

            logger.info("Successfully processed query and generated results.")
            # Ensure insights_text_combined is a string for dcc.Markdown
            insights_display_component = dcc.Markdown(str(insights_text_combined) if insights_text_combined is not None else "")

            return sql_query_md, results_md_component, charts_components, insights_display_component, "" # Clear query input

        except Exception as e:
            logger.error(f"Unhandled error in handle_query_submission: {e}", exc_info=True)
            # Default error message for unexpected issues
            error_sql_display = "Error processing request."
            error_table_display = f"An unexpected error occurred: {str(e)}"
            return error_sql_display, error_table_display, [], "", query_text


    @app.callback(
        Output('query-input', 'value', allow_duplicate=True),
        Input('clear-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_query_input(n_clicks_clear):
        if n_clicks_clear:
            return ""
        raise PreventUpdate
