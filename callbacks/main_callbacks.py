from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash

from agents.data_analyst_agent import DataAnalystAgent

def register_callbacks(app):
    @app.callback(
        [Output('query-results-table', 'children'),
         Output('query-input', 'value')],
        [Input('submit-button', 'n_clicks')],
        [State('query-input', 'value')]
    )
    def update_output(n_clicks, value):
        if n_clicks and value:
            # Instantiate the DataAnalystAgent
            analyst_agent = DataAnalystAgent()

            # Process the query using the agent
            result_markdown = analyst_agent.process(value)

            # Display the results
            return [html.Div([
                html.H5("Query Results:"),
                dcc.Markdown(result_markdown, dangerously_allow_html=True)
            ])], ""
        
        return dash.no_update, dash.no_update

    @app.callback(
        Output('query-input', 'value', allow_duplicate=True),
        Input('clear-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_query_input(n_clicks):
        if n_clicks:
            return ""
        return dash.no_update
