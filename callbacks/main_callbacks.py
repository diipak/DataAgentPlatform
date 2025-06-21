import os
import json
import logging
import dash # Ensure dash is imported
from dash import dcc, html, callback_context, dash_table # Add callback_context
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

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

    # New chat interface callbacks with real agent integration
    @app.callback(
        [Output('chat-messages', 'children'),
         Output('main-visualization', 'children'),
         Output('data-table', 'children'),
         Output('key-insights', 'children'),
         Output('chat-input', 'value')],
        [Input('send-button', 'n_clicks'),
         Input('chat-input', 'n_submit'),
         Input('suggestion-1', 'n_clicks'),
         Input('suggestion-2', 'n_clicks'),
         Input('suggestion-3', 'n_clicks'),
         Input('suggestion-4', 'n_clicks')],
        [State('chat-input', 'value'),
         State('store-chat-messages', 'data'),
         State('dataset-dropdown', 'value')],
        prevent_initial_call=True
    )
    def handle_chat_interaction(send_clicks, input_submit, sugg1_clicks, sugg2_clicks, sugg3_clicks, sugg4_clicks, 
                               input_value, chat_history, selected_dataset):
        import plotly.graph_objects as go
        from dash import dash_table
        import pandas as pd
        from datetime import datetime
        
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Determine the message based on trigger
        message = ""
        if trigger_id == 'suggestion-1':
            message = "Analyze rice production trends over time"
        elif trigger_id == 'suggestion-2':
            message = "Compare wheat vs rice yield efficiency"
        elif trigger_id == 'suggestion-3':
            message = "Which states have highest crop productivity?"
        elif trigger_id == 'suggestion-4':
            message = "Find correlations in agricultural data"
        elif trigger_id in ['send-button', 'chat-input']:
            message = input_value
        
        if not message:
            raise PreventUpdate
        
        # Initialize chat history if None
        if not chat_history:
            chat_history = []
        
        # Add user message
        chat_history.append({
            'type': 'user',
            'content': message,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
        # Process with real agents if PROJECT_ID is available and dataset is selected
        bot_response = ""
        visualization = html.Div("No visualization available", className="text-muted")
        data_table = html.Div("No data available", className="text-muted")
        insights_elements = []
        
        try:
            if PROJECT_ID and selected_dataset:
                logger.info(f"Processing query with agents: '{message}' for dataset: {selected_dataset}")
                
                # Use DataAnalystAgent to process the query
                try:
                    data_analyst = DataAnalystAgent(project_id=PROJECT_ID)
                    logger.info(f"DataAnalystAgent initialized successfully")
                except Exception as agent_error:
                    logger.error(f"Error initializing DataAnalystAgent: {agent_error}")
                    if "credentials" in str(agent_error).lower():
                        bot_response = f"Authentication issue: Please check your Google Cloud credentials are properly configured."
                    elif "permission" in str(agent_error).lower():
                        bot_response = f"Permission issue: Please ensure your service account has BigQuery access permissions."
                    elif "project" in str(agent_error).lower():
                        bot_response = f"Project issue: Please verify the Google Cloud Project ID is correct."
                    else:
                        bot_response = f"Configuration issue: {str(agent_error)}"
                    
                if 'data_analyst' in locals() and hasattr(data_analyst, 'schema_agent') and hasattr(data_analyst, 'bigquery_tool') and data_analyst.schema_agent and data_analyst.bigquery_tool:
                    # Get dataset schema
                    dataset_schema = data_analyst.schema_agent.get_full_dataset_schema(selected_dataset)
                    
                    if not dataset_schema:
                        bot_response = f"The dataset '{selected_dataset}' appears to be empty or could not be accessed. This could be because:\n• The dataset has no tables yet\n• Access permissions need to be configured\n• The dataset doesn't exist\n\nOnce you add tables to the dataset, I'll be able to analyze your data!"
                    else:
                        # Get the first table from the dataset schema for processing
                        first_table = list(dataset_schema.keys())[0] if dataset_schema else None
                        if not first_table:
                            bot_response = f"The dataset '{selected_dataset}' was found but contains no tables yet. Please add some tables with data, and I'll be ready to help you analyze it!"
                        else:
                            # Construct full table reference: dataset.table
                            full_table_ref = f"{selected_dataset}.{first_table}"
                            
                            # Process the query
                            result = data_analyst.process(
                                query=message,
                                dataset_schema=dataset_schema,
                                project_id=data_analyst.project_id,
                                dataset_id=full_table_ref
                            )
                            
                            if result.get('results_df') is not None and result.get('error') is None:
                                df = result.get('results_df')
                                sql_query = result.get('sql_query', '')
                                
                                # Generate intelligent bot response
                                summary_stats = f"Found {len(df)} records with {len(df.columns)} columns"
                                if len(df) > 0:
                                    numeric_cols = df.select_dtypes(include=['number']).columns
                                    if len(numeric_cols) > 0:
                                        avg_val = df[numeric_cols[0]].mean() if not df[numeric_cols[0]].isna().all() else 0
                                        summary_stats += f". Average {numeric_cols[0]}: {avg_val:.2f}"
                                
                                bot_response = f"""📊 **Analysis Complete!**

{summary_stats}

**Query executed:** `{sql_query}`

🔍 **Key findings:**
• Dataset contains agricultural data across different states and years
• Multiple crop types with area, production, and yield metrics
• Data spans from various agricultural seasons

The visualization and detailed insights are shown on the right panel. Feel free to ask more specific questions about the data!"""
                                
                                # Create intelligent visualization based on data type
                                if df is not None and not df.empty:
                                    try:
                                        # Determine best visualization type
                                        if 'count' in message.lower() or 'total' in message.lower():
                                            # For count queries, show a metric card
                                            fig = go.Figure(go.Indicator(
                                                mode = "number",
                                                value = df.iloc[0, 0] if len(df) == 1 else len(df),
                                                title = {"text": "Total Records" if len(df) > 1 else "Count"},
                                                number = {'font': {'size': 60, 'color': '#5dade2'}},
                                                domain = {'x': [0, 1], 'y': [0, 1]}
                                            ))
                                            fig.update_layout(
                                                paper_bgcolor='rgba(0,0,0,0)',
                                                plot_bgcolor='rgba(0,0,0,0)',
                                                font=dict(color='white'),
                                                height=300
                                            )
                                        elif len(df.columns) >= 2:
                                            # For data queries, create appropriate charts
                                            numeric_cols = df.select_dtypes(include=['number']).columns
                                            if len(numeric_cols) >= 1:
                                                x_col = df.columns[0]
                                                y_col = numeric_cols[0]
                                                
                                                if len(df) <= 20:
                                                    # Bar chart for small datasets
                                                    fig = go.Figure(data=[
                                                        go.Bar(x=df[x_col].astype(str), y=df[y_col], 
                                                              marker_color='rgba(93, 173, 226, 0.8)')
                                                    ])
                                                    fig.update_layout(
                                                        title=f"{y_col} by {x_col}",
                                                        xaxis_title=x_col,
                                                        yaxis_title=y_col,
                                                        plot_bgcolor='rgba(0,0,0,0)',
                                                        paper_bgcolor='rgba(0,0,0,0)',
                                                        font=dict(color='white'),
                                                        showlegend=False,
                                                        margin=dict(l=60, r=40, t=80, b=120),
                                                        height=400
                                                    )
                                                    fig.update_xaxes(
                                                        tickangle=45,
                                                        gridcolor='rgba(255,255,255,0.1)'
                                                    )
                                                    fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
                                                else:
                                                    # Line chart for larger datasets
                                                    fig = go.Figure(data=[
                                                        go.Scatter(x=df[x_col], y=df[y_col], 
                                                                  mode='lines+markers', 
                                                                  line=dict(color='#5dade2'))
                                                    ])
                                                
                                                fig.update_layout(
                                                    title=f"{y_col} by {x_col}",
                                                    xaxis_title=x_col,
                                                    yaxis_title=y_col,
                                                    plot_bgcolor='rgba(0,0,0,0)',
                                                    paper_bgcolor='rgba(0,0,0,0)',
                                                    font=dict(color='white'),
                                                    showlegend=False,
                                                    margin=dict(l=60, r=40, t=80, b=100),
                                                    height=400
                                                )
                                                # Fix x-axis label overlapping
                                                fig.update_xaxes(
                                                    tickangle=45,
                                                    tickmode='linear',
                                                    dtick=max(1, len(df) // 10) if len(df) > 10 else 1,
                                                    gridcolor='rgba(255,255,255,0.1)'
                                                )
                                                fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
                                            else:
                                                # Text data visualization
                                                fig = go.Figure()
                                                fig.add_annotation(
                                                    text=f"Showing {len(df)} text records<br>Use the data table below for details",
                                                    xref="paper", yref="paper",
                                                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                                                    showarrow=False,
                                                    font=dict(size=20, color='white')
                                                )
                                                fig.update_layout(
                                                    plot_bgcolor='rgba(0,0,0,0)',
                                                    paper_bgcolor='rgba(0,0,0,0)',
                                                    xaxis=dict(visible=False),
                                                    yaxis=dict(visible=False)
                                                )
                                        
                                        visualization = dcc.Graph(figure=fig, config={'displayModeBar': False})
                                    except Exception as viz_error:
                                        logger.error(f"Visualization error: {viz_error}")
                                        visualization = html.Div("Chart generation temporarily unavailable", className="text-muted")
                                
                                # Create enhanced data table with better formatting
                                try:
                                    # Limit columns for display if too many
                                    display_df = df.head(50)  # Show more rows
                                    if len(df.columns) > 8:
                                        display_df = display_df.iloc[:, :8]  # Show first 8 columns
                                    
                                    data_table = dash_table.DataTable(
                                        data=display_df.to_dict('records'),
                                        columns=[{'name': col, 'id': col} for col in display_df.columns],
                                        style_cell={
                                            'textAlign': 'left', 
                                            'backgroundColor': 'rgba(255,255,255,0.05)', 
                                            'color': 'white', 
                                            'border': '1px solid rgba(255,255,255,0.1)',
                                            'padding': '10px',
                                            'fontSize': '14px'
                                        },
                                        style_header={
                                            'backgroundColor': 'rgba(93, 173, 226, 0.8)', 
                                            'fontWeight': 'bold',
                                            'color': 'white'
                                        },
                                        style_data={'backgroundColor': 'transparent'},
                                        page_size=20,
                                        fixed_rows={'headers': True}
                                    )
                                except Exception as table_error:
                                    logger.error(f"Table creation error: {table_error}")
                                    data_table = html.Div("Data table temporarily unavailable", className="text-muted")
                                
                                # Generate comprehensive insights
                                try:
                                    insights_elements = []
                                    
                                    # Basic data insights
                                    insights_elements.append(
                                        html.Div(className="insight-item", children=[
                                            html.I(className="insight-bullet fas fa-database"),
                                            html.Div(f"Dataset contains {len(df)} records across {len(df.columns)} columns", className="insight-text")
                                        ])
                                    )
                                    
                                    # Column type analysis
                                    numeric_cols = len(df.select_dtypes(include=['number']).columns)
                                    text_cols = len(df.select_dtypes(include=['object']).columns)
                                    if numeric_cols > 0:
                                        insights_elements.append(
                                            html.Div(className="insight-item", children=[
                                                html.I(className="insight-bullet fas fa-calculator"),
                                                html.Div(f"{numeric_cols} numeric columns available for mathematical analysis", className="insight-text")
                                            ])
                                        )
                                    
                                    if text_cols > 0:
                                        insights_elements.append(
                                            html.Div(className="insight-item", children=[
                                                html.I(className="insight-bullet fas fa-font"),
                                                html.Div(f"{text_cols} text columns for categorical analysis", className="insight-text")
                                            ])
                                        )
                                    
                                    # Data quality insights
                                    if len(df) > 0:
                                        null_cols = df.isnull().sum()
                                        cols_with_nulls = null_cols[null_cols > 0]
                                        if len(cols_with_nulls) == 0:
                                            insights_elements.append(
                                                html.Div(className="insight-item", children=[
                                                    html.I(className="insight-bullet fas fa-check-circle"),
                                                    html.Div("Excellent data quality - no missing values detected", className="insight-text")
                                                ])
                                            )
                                        else:
                                            insights_elements.append(
                                                html.Div(className="insight-item", children=[
                                                    html.I(className="insight-bullet fas fa-exclamation-triangle"),
                                                    html.Div(f"{len(cols_with_nulls)} columns have missing values that may need attention", className="insight-text")
                                                ])
                                            )
                                    
                                    # Statistical insights for numeric data
                                    numeric_cols = df.select_dtypes(include=['number']).columns
                                    if len(numeric_cols) > 0:
                                        for col in numeric_cols[:2]:  # Show insights for first 2 numeric columns
                                            if not df[col].isna().all():
                                                min_val = df[col].min()
                                                max_val = df[col].max()
                                                insights_elements.append(
                                                    html.Div(className="insight-item", children=[
                                                        html.I(className="insight-bullet fas fa-chart-line"),
                                                        html.Div(f"{col}: ranges from {min_val:.2f} to {max_val:.2f}", className="insight-text")
                                                    ])
                                                )
                                    
                                    # Temporal insights if year column exists
                                    year_cols = [col for col in df.columns if 'year' in col.lower()]
                                    if year_cols and len(df) > 0:
                                        year_col = year_cols[0]
                                        year_range = f"{df[year_col].min():.0f} to {df[year_col].max():.0f}"
                                        insights_elements.append(
                                            html.Div(className="insight-item", children=[
                                                html.I(className="insight-bullet fas fa-calendar"),
                                                html.Div(f"Time series data spanning {year_range}", className="insight-text")
                                            ])
                                        )
                                    
                                except Exception as insights_error:
                                    logger.error(f"Insights generation error: {insights_error}")
                                    insights_elements = [
                                        html.Div(className="insight-item", children=[
                                            html.I(className="insight-bullet fas fa-info-circle"),
                                            html.Div(f"Successfully retrieved {len(df)} records", className="insight-text")
                                        ])
                                    ]
                            else:
                                error_msg = result.get('error', 'Unknown error')
                                sql_query = result.get('sql_query', 'N/A')
                                bot_response = f"Sorry, I encountered an error processing your query: {error_msg}"
                elif 'data_analyst' in locals():
                    # Agent was created but some components failed to initialize
                    if not hasattr(data_analyst, 'schema_agent') or not data_analyst.schema_agent:
                        bot_response = "Schema agent failed to initialize. Please check BigQuery access permissions and project configuration."
                    elif not hasattr(data_analyst, 'bigquery_tool') or not data_analyst.bigquery_tool:
                        bot_response = "BigQuery tool failed to initialize. Please check your Google Cloud credentials and project access."
                    else:
                        bot_response = "Some agent components failed to initialize. Please check your Google Cloud configuration."
                else:
                    bot_response = "Failed to initialize data analysis agents. Please check your Google Cloud Project configuration and credentials."
            else:
                bot_response = "Please select a dataset first to analyze your data."
                
        except Exception as e:
            logger.error(f"Error in chat interaction: {e}")
            bot_response = f"Sorry, I encountered an error: {str(e)}"
        
        # Add bot response to chat history
        chat_history.append({
            'type': 'bot',
            'content': bot_response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
        # Create chat messages elements - show all messages for conversation flow
        chat_elements = []
        for msg in chat_history:  # Show ALL messages for proper conversation
            if msg['type'] == 'user':
                chat_elements.append(
                    html.Div(className="user-message", children=[
                        html.Div(msg['content'], className="message-content"),
                        html.Div(msg['timestamp'], className="message-timestamp")
                    ])
                )
            else:
                # Use dcc.Markdown for rich bot responses
                chat_elements.append(
                    html.Div(className="bot-message", children=[
                        dcc.Markdown(msg['content'], className="message-content"),
                        html.Div(msg['timestamp'], className="message-timestamp")
                    ])
                )
        
        return chat_elements, visualization, data_table, insights_elements, ""

    # Store chat messages - synchronized with real agent callback
    @app.callback(
        Output('store-chat-messages', 'data'),
        [Input('send-button', 'n_clicks'),
         Input('chat-input', 'n_submit'),
         Input('suggestion-1', 'n_clicks'),
         Input('suggestion-2', 'n_clicks'),
         Input('suggestion-3', 'n_clicks'),
         Input('suggestion-4', 'n_clicks')],
        [State('chat-input', 'value'),
         State('store-chat-messages', 'data')],
        prevent_initial_call=True
    )
    def update_chat_store(send_clicks, input_submit, sugg1_clicks, sugg2_clicks, sugg3_clicks, sugg4_clicks, 
                         input_value, chat_history):
        from datetime import datetime
        
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Determine the message based on trigger
        message = ""
        if trigger_id == 'suggestion-1':
            message = "Analyze rice production trends over time"
        elif trigger_id == 'suggestion-2':
            message = "Compare wheat vs rice yield efficiency"
        elif trigger_id == 'suggestion-3':
            message = "Which states have highest crop productivity?"
        elif trigger_id == 'suggestion-4':
            message = "Find correlations in agricultural data"
        elif trigger_id in ['send-button', 'chat-input']:
            message = input_value
        
        if not message:
            raise PreventUpdate
        
        # Initialize chat history if None
        if not chat_history:
            chat_history = []
        
        # Add user message - bot response will be added by the main callback
        chat_history.append({
            'type': 'user',
            'content': message,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
        return chat_history
    
    # New visible dataset dropdown callbacks
    @app.callback(
        [Output('dataset-dropdown-visible', 'options'),
         Output('dataset-dropdown-visible', 'value'),
         Output('dataset-load-status-visible', 'children')],
        [Input('load-datasets-button-visible', 'n_clicks')],
        prevent_initial_call=True
    )
    def load_datasets_visible(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        
        if not PROJECT_ID:
            return [], None, "Error: GOOGLE_CLOUD_PROJECT not configured."
        
        try:
            logger.info("Loading datasets for visible dropdown")
            schema_agent = SchemaAgent(project_id=PROJECT_ID)
            if not schema_agent.connector:
                return [], None, "Error: Failed to connect to BigQuery."
            
            datasets = schema_agent.get_available_datasets()
            if not datasets:
                return [], None, "No datasets found."
            
            options = [{'label': ds_id, 'value': ds_id} for ds_id in datasets]
            default_value = options[0]['value'] if options else None
            logger.info(f"Loaded {len(datasets)} datasets for visible dropdown.")
            return options, default_value, f"Successfully loaded {len(datasets)} datasets."
            
        except Exception as e:
            logger.error(f"Error loading datasets for visible dropdown: {e}")
            return [], None, f"Error loading datasets: {str(e)}"
    
    # Sync the visible dropdown with the hidden one used by other callbacks
    @app.callback(
        Output('dataset-dropdown', 'value', allow_duplicate=True),
        [Input('dataset-dropdown-visible', 'value')],
        prevent_initial_call=True
    )
    def sync_dataset_selection(visible_value):
        return visible_value
