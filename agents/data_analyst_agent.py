# agents/data_analyst_agent.py

import os

from google.adk.agents import Agent
from vertexai.generative_models import GenerativeModel

from adk_tools.bigquery_tool import BigQueryTool

class DataAnalystAgent(Agent):
    def __init__(self):
        super().__init__()
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file.")
        self.bigquery_tool = BigQueryTool(project_id=project_id)
        self.model = GenerativeModel("gemini-1.0-pro")
        # TODO: Make this table name configurable in the UI
        self.target_table = "bigquery-public-data.samples.shakespeare"

    def process(self, query: str) -> str:
        """
        Processes a natural language query, converts it to a SQL query,
        executes it, and returns the results as a Markdown table.
        """
        # 1. Get table schema to provide context to the LLM.
        schema = self.bigquery_tool.get_schema(self.target_table)
        if 'error' in schema:
            return f"Could not retrieve schema for table {self.target_table}: {schema['error']}"

        # 2. Construct a prompt for the LLM to generate a SQL query.
        prompt = f"""
        You are a Google BigQuery expert. Your task is to convert a natural language question into a valid BigQuery SQL query.

        Here is the schema of the table `{self.target_table}`:
        Columns: {schema['columns']}

        Natural language question:
        '{query}'

        Please provide only the BigQuery SQL query that answers this question. Do not include any explanation or introductory text.
        """

        # 3. Call the LLM to generate the SQL query.
        try:
            response = self.model.generate_content(prompt)
            # Clean up the response to get only the SQL query
            sql_query = response.text.strip().replace("```sql", "").replace("```", "")
        except Exception as e:
            return f"Error generating SQL query: {e}"

        # 4. Execute the generated SQL query.
        try:
            results_df = self.bigquery_tool.execute_query(sql_query)
            if not results_df.empty:
                return results_df.to_markdown(index=False)
            else:
                return f"The query '{sql_query}' executed successfully, but returned no results."
        except Exception as e:
            return f"An error occurred while executing the generated SQL query:\n`{sql_query}`\n\n**Error details:**\n{e}"
