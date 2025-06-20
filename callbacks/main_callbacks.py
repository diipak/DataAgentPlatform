import os
import json
import logging
import dash # Ensure dash is imported
from dash import dcc, html, callback_context # Add callback_context
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from agents import SchemaAgent, DataAnalystAgent, VisualizationAgent

logger = logging.getLogger(__name__)

try:
    PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")
except KeyError:
    logger.error("CRITICAL: GOOGLE_CLOUD_PROJECT environment variable is not set.")
    PROJECT_ID = None

def register_callbacks(app):

    # Callback for loading datasets (remains largely the same, ensure it doesn't conflict)
    @app.callback(
        [Output('dataset-dropdown', 'options'),
         Output('dataset-dropdown', 'value'),
         Output('dataset-load-status', 'children'),
         Output('global-error-alert', 'children'),
         Output('global-error-alert', 'is_open')],
        [Input('load-datasets-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def load_datasets(n_clicks):
        # ... (existing load_datasets logic from previous turn) ...
        # This function's logic is not changed in this subtask,
        # but ensure it's here and complete from the previous version.
        if not n_clicks:
            raise PreventUpdate
        error_message = None
        is_error = False
        if not PROJECT_ID:
            error_message = "Error: GOOGLE_CLOUD_PROJECT not configured."
            is_error = True
            return [], None, "", error_message, is_error
        try:
            logger.info("Instantiating SchemaAgent to load datasets.")
            schema_agent = SchemaAgent(project_id=PROJECT_ID)
            if not schema_agent.connector:
                error_message = "Error: SchemaAgent failed to connect to BigQuery. Check GCP setup and agent logs."
                is_error = True
                return [], None, "", error_message, is_error
            datasets = schema_agent.get_available_datasets()
            if not datasets:
                return [], None, "No datasets found or project has no queryable datasets.", None, False
            options = [{'label': ds_id, 'value': ds_id} for ds_id in datasets]
            default_value = options[0]['value'] if options else None
            logger.info(f"Loaded {len(datasets)} datasets for dropdown.")
            return options, default_value, f"Successfully loaded {len(datasets)} datasets.", None, False
        except Exception as e:
            logger.error(f"Error loading datasets: {e}", exc_info=True)
            error_message = f"Error loading datasets: {str(e)}"
            is_error = True
            return [], None, "", error_message, is_error


    # Main query submission callback - MODIFIED to add SQL to dcc.Store
    @app.callback(
        [Output('sql-query-display', 'children'),
         Output('query-results-table', 'children'),
         Output('charts-display-area', 'children'),
         Output('insights-display-area', 'children'),
         Output('query-input', 'value', allow_duplicate=True),
         Output('global-error-alert', 'children', allow_duplicate=True),
         Output('global-error-alert', 'is_open', allow_duplicate=True),
         Output('store-generated-sql', 'data')], # New output for storing SQL
        [Input('submit-button', 'n_clicks')],
        [State('query-input', 'value'),
         State('dataset-dropdown', 'value')],
        prevent_initial_call=True
    )
    def handle_query_submission(n_clicks, query_text, selected_dataset):
        # ... (existing setup and initial error checks from previous turn) ...
        # This function needs to be complete from the previous version.
        # The main addition is setting 'store-generated-sql.data'.

        if not n_clicks:
            raise PreventUpdate

        no_sql_md = ""
        no_table_md = ""
        no_charts_list = []
        no_insights_md = ""
        error_msg_str = None
        is_error_bool = False
        stored_sql_str = "" # Initialize stored SQL

        if not PROJECT_ID:
            error_msg_str = "Error: GCP Project not configured. Please set GOOGLE_CLOUD_PROJECT."
            is_error_bool = True
            return no_sql_md, no_table_md, no_charts_list, no_insights_md, query_text, error_msg_str, is_error_bool, stored_sql_str
        
        if not query_text:
            error_msg_str = "Error: Query cannot be empty."
            is_error_bool = True
            return no_sql_md, no_table_md, no_charts_list, no_insights_md, query_text, error_msg_str, is_error_bool, stored_sql_str

        if not selected_dataset:
            error_msg_str = "Error: Please select a dataset first."
            is_error_bool = True
            return no_sql_md, no_table_md, no_charts_list, no_insights_md, query_text, error_msg_str, is_error_bool, stored_sql_str

        logger.info(f"Handling query: '{query_text}' for dataset: '{selected_dataset}'")

        try:
            schema_agent = SchemaAgent(project_id=PROJECT_ID)
            data_analyst_agent = DataAnalystAgent(project_id=PROJECT_ID)
            visualization_agent = VisualizationAgent()

            if not schema_agent.connector or not data_analyst_agent.connector:
                error_msg_str = "Error: Key agent(s) failed to connect to BigQuery. Check GCP setup and agent logs."
                is_error_bool = True
                return no_sql_md, no_table_md, no_charts_list, no_insights_md, query_text, error_msg_str, is_error_bool, stored_sql_str

            full_schema = schema_agent.get_full_dataset_schema(selected_dataset)
            if not full_schema or any(table_info.get('error') for table_info in full_schema.values() if isinstance(table_info, dict)):
                # ... (error handling for schema) ...
                schema_errors_detail = {k: v.get('error') for k, v in full_schema.items() if isinstance(v, dict) and v.get('error')}
                error_detail_msg = f" Could not retrieve schema for some tables: {schema_errors_detail}" if schema_errors_detail else ""
                error_msg_str = f"Error: Failed to get complete schema for dataset {selected_dataset}.{error_detail_msg}"
                is_error_bool = True
                logger.error(error_msg_str)
                return no_sql_md, no_table_md, no_charts_list, no_insights_md, query_text, error_msg_str, is_error_bool, stored_sql_str


            analysis_result = data_analyst_agent.process(
                query=query_text, dataset_schema=full_schema, project_id=PROJECT_ID, dataset_id=selected_dataset
            )

            # Store the generated SQL
            stored_sql_str = analysis_result.get('sql_query', "") # Store SQL here
            sql_display_content = dcc.Markdown(f"```sql\n{stored_sql_str or 'N/A'}\n```")

            if analysis_result.get('error'):
                error_msg_str = f"Error during data analysis: {analysis_result['error']}"
                is_error_bool = True
                logger.error(error_msg_str)
                return sql_display_content, no_table_md, no_charts_list, no_insights_md, query_text, error_msg_str, is_error_bool, stored_sql_str

            results_md_content = dcc.Markdown(analysis_result['results_markdown'])
            charts_components_content = []
            insights_text_combined_content = ""

            if analysis_result['results_df'] is not None and not analysis_result['results_df'].empty:
                viz_result = visualization_agent.generate_visualizations(
                    data_df=analysis_result['results_df'], query=query_text
                )
                for chart_json_str in viz_result.get('charts', []):
                    try:
                        chart_fig = json.loads(chart_json_str)
                        charts_components_content.append(dcc.Graph(figure=chart_fig))
                    except Exception as e:
                        logger.error(f"Error loading chart JSON: {e}")
                        charts_components_content.append(html.Pre(f"Error loading chart: {e}"))
                insights_text_combined_content = dcc.Markdown(viz_result.get('insights_text', ""))
            else:
                insights_text_combined_content = dcc.Markdown("Query returned no data or an error occurred; no visualizations generated.")

            return sql_display_content, results_md_content, charts_components_content, insights_text_combined_content, "", None, False, stored_sql_str

        except Exception as e:
            logger.error(f"Unhandled error in handle_query_submission: {e}", exc_info=True)
            error_msg_str = f"An unexpected server error occurred: {str(e)}"
            is_error_bool = True
            sql_query_val_err = "" # Default to empty string for stored SQL in this specific error case
            if 'analysis_result' in locals() and analysis_result and isinstance(analysis_result, dict) and analysis_result.get('sql_query'):
                 sql_query_val_err = analysis_result.get('sql_query')

            # Ensure sql_err_display is a valid Dash component (e.g., dcc.Markdown or html.Div)
            sql_err_display_content = f"```sql\n{sql_query_val_err or 'N/A'}\n```"
            sql_err_display = dcc.Markdown(sql_err_display_content)

            # Store SQL even if there's a later error
            return sql_err_display, no_table_md, no_charts_list, no_insights_md, query_text, error_msg_str, is_error_bool, sql_query_val_err


    # New callback for SQL feedback
    @app.callback(
        Output('sql-feedback-status', 'children'),
        [Input('sql-feedback-up-button', 'n_clicks'),
         Input('sql-feedback-down-button', 'n_clicks')],
        [State('store-generated-sql', 'data')],
        prevent_initial_call=True
    )
    def handle_sql_feedback(n_clicks_up, n_clicks_down, stored_sql):
        if not n_clicks_up and not n_clicks_down:
            raise PreventUpdate

        ctx = callback_context
        if not ctx.triggered: # Should not happen with the condition above, but good practice
            raise PreventUpdate

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        feedback_type = "positive" if button_id == "sql-feedback-up-button" else "negative"

        if stored_sql:
            logger.info(f"SQL Feedback received: '{feedback_type}' for SQL query: \n{stored_sql}")
            # In a real app, this feedback would be stored more persistently.
            return f"Thanks for your {feedback_type} feedback!"
        else:
            logger.warning(f"SQL Feedback ({feedback_type}) given, but no SQL query was found in the store.")
            return "Could not record feedback: no query found."

    # Clear button callback (remains unchanged)
    @app.callback(
        Output('query-input', 'value', allow_duplicate=True),
        Input('clear-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_query_input(n_clicks_clear):
        if n_clicks_clear:
            return ""
        raise PreventUpdate
