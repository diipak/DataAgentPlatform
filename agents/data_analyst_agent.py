# agents/data_analyst_agent.py

import os

from google.adk.agents import Agent

from adk_tools.bigquery_tool import BigQueryTool

class DataAnalystAgent(Agent):
    def __init__(self):
        super().__init__()
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file.")
        self.bigquery_tool = BigQueryTool(project_id=project_id)

    def process(self, query: str) -> str:
        """
        Processes a natural language query to generate and execute a BigQuery SQL query.

        Args:
            query: The natural language query from the user.

        Returns:
            A string containing the query result or an error message.
        """
        try:
            # For now, we'll just pass the query through to the tool.
            # In the future, this is where a language model would generate
            # a SQL query from the natural language input.
            sql_query = self.generate_sql(query)
            
            # Execute the query
            result_df = self.bigquery_tool.execute_query(sql_query)
            return result_df.to_markdown()

        except Exception as e:
            return f"An error occurred: {e}"

    def generate_sql(self, natural_language_query: str) -> str:
        """
        This is a placeholder for a language model call that would convert
        a natural language query into a SQL query.

        For now, it will just return the query as is, assuming the user
        is entering a valid SQL query.
        """
        # TODO: Integrate a language model (e.g., Vertex AI's Gemini)
        # to translate natural language to SQL.
        print(f"--- Generating SQL for query: '{natural_language_query}' ---")
        return natural_language_query
