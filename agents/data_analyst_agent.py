# agents/data_analyst_agent.py

import os
import logging # Added import

from google.adk.agents import Agent
from vertexai.generative_models import GenerativeModel

from adk_tools.bigquery_tool import BigQueryTool
from connectors.bigquery_connector import BigQueryConnector # Added import
from agents.schema_agent import SchemaAgent # Added import

logger = logging.getLogger(__name__) # Added logger initialization

class DataAnalystAgent(Agent):
    def __init__(self):
        super().__init__()
        logger.info("Initializing DataAnalystAgent...")
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            logger.error("GOOGLE_CLOUD_PROJECT environment variable not set.")
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file or equivalent.")

        try:
            logger.info(f"Attempting to initialize BigQueryConnector with project_id: {project_id}")
            self.connector = BigQueryConnector(project_id=project_id)
            logger.info("BigQueryConnector initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize BigQueryConnector: {e}")
            raise  # Or handle more gracefully depending on requirements

        try:
            logger.info(f"Attempting to initialize SchemaAgent with project_id: {project_id}")
            self.schema_agent = SchemaAgent(project_id=project_id) # Initialize SchemaAgent
            logger.info("SchemaAgent initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize SchemaAgent: {e}")
            # Decide if this is critical or if the agent can operate without it
            # For now, let's make it non-critical for basic query processing if target_table is fixed
            self.schema_agent = None # Or raise e if SchemaAgent is essential

        logger.info("Initializing BigQueryTool with the connector.")
        self.bigquery_tool = BigQueryTool(connector=self.connector) # Pass connector instance

        self.model = GenerativeModel("gemini-1.0-pro")
        logger.info("DataAnalystAgent initialized.")

    def process(self, query: str, dataset_schema: dict, project_id: str, dataset_id: str) -> dict:
        """
        Processes a natural language query, converts it to a SQL query using the provided dataset schema,
        executes it, and returns the results along with the SQL query.
        """
        logger.info(f"Processing query: '{query}' for dataset: {project_id}.{dataset_id}")

        return_value = {
            'sql_query': None,
            'results_df': None,
            'results_markdown': None,
            'error': None
        }

        # 1. Format the schema for the prompt
        formatted_schema_parts = []
        if not dataset_schema:
            logger.warning(f"Dataset schema for {project_id}.{dataset_id} is empty or None.")
            # Fallback or error if schema is critical - for now, we'll let it proceed and LLM might fail
            formatted_schema_parts.append("No schema information available for this dataset.")
        else:
            for table_name, table_info in dataset_schema.items():
                if table_info and 'columns' in table_info and table_info['columns']:
                    columns_str = ", ".join([f"{col['name']} ({col['type']})" for col in table_info['columns']])
                    formatted_schema_parts.append(f"Table: {table_name}, Columns: [{columns_str}]")
                else:
                    formatted_schema_parts.append(f"Table: {table_name}, Columns: (Schema not available or table is empty)")

        formatted_schema_string = "\n".join(formatted_schema_parts)

        # 2. Construct a prompt for the LLM to generate a SQL query.
        prompt = f"""
        You are a Google BigQuery expert. Your task is to convert a natural language question into a valid BigQuery SQL query that targets the dataset '{dataset_id}' in project '{project_id}'.

        Here is the schema of the dataset '{dataset_id}':
        {formatted_schema_string}

        Natural language question:
        '{query}'

        Based on the question and the provided dataset schema, generate a single, valid BigQuery SQL query.
        The query should explicitly reference tables with their full path if needed (e.g., `{project_id}.{dataset_id}.table_name`), or assume the query will be run in the context of the specified project and dataset.
        Provide only the BigQuery SQL query. Do not include any explanation or introductory text.
        """
        logger.debug(f"Generated prompt for LLM: {prompt}")

        # 3. Call the LLM to generate the SQL query.
        try:
            logger.info("Generating SQL query using LLM...")
            response = self.model.generate_content(prompt)
            # Clean up the response to get only the SQL query
            sql_query = response.text.strip().replace("```sql", "").replace("```", "").replace("`", "")
            logger.info(f"Generated SQL query: {sql_query}")
            return_value['sql_query'] = sql_query
        except Exception as e:
            logger.error(f"Error generating SQL query with LLM: {e}")
            return_value['error'] = f"Error generating SQL query: {e}"
            return return_value

        # 4. Execute the generated SQL query.
        try:
            logger.info(f"Executing SQL query: {sql_query}")
            results_df = self.bigquery_tool.execute_query(sql_query)
            return_value['results_df'] = results_df

            if results_df is not None and not results_df.empty:
                logger.info(f"Query executed successfully, returned {len(results_df)} rows.")
                return_value['results_markdown'] = results_df.to_markdown(index=False)
            elif results_df is not None: # Empty DataFrame
                logger.info(f"Query '{sql_query}' executed successfully, but returned no results.")
                return_value['results_markdown'] = f"The query '{sql_query}' executed successfully, but returned no results."
            else: # Should not happen if execute_query raises or returns DataFrame
                logger.error(f"Query execution returned None for: {sql_query}")
                # This case might indicate an issue with bigquery_tool.execute_query if it doesn't raise an exception
                # but returns None, which it shouldn't based on current connector implementation.
                return_value['error'] = f"Query execution failed or returned an unexpected result (None) for: {sql_query}"

        except Exception as e:
            logger.error(f"Error executing SQL query '{sql_query}': {e}")
            return_value['error'] = f"An error occurred while executing the generated SQL query:\n`{sql_query}`\n\n**Error details:**\n{e}"

        return return_value
