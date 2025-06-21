# agents/data_analyst_agent.py

import os
import logging # Added import

from google.adk.agents import Agent
from vertexai.generative_models import GenerativeModel
from typing import Dict, Any, Optional # Ensure Optional is imported

from adk_tools.bigquery_tool import BigQueryTool
from connectors.bigquery_connector import BigQueryConnector
from agents.schema_agent import SchemaAgent

logger = logging.getLogger(__name__)

class DataAnalystAgent(Agent):
    def __init__(self, project_id: Optional[str] = None, name: Optional[str] = "DataAnalystAgent"): # Add name parameter
        super().__init__(name=name, description="Agent for natural language to SQL conversion and data analysis.") # Pass name and description
        logger.info(f"Initializing {name}...")

        if project_id is None:
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

        if not project_id:
            logger.error(f"{name}: GOOGLE_CLOUD_PROJECT environment variable not set and no project_id provided.")
            raise ValueError(f"{name}: GOOGLE_CLOUD_PROJECT environment variable not set and no project_id provided.")

        # Store project_id in a way that works with ADK Agent
        self._project_id = project_id
        try:
            self._connector = BigQueryConnector(project_id=self._project_id) # Connector for the tool
            self._bigquery_tool = BigQueryTool(connector=self._connector)
            logger.info(f"{name} initialized BigQueryTool with project_id: {self._project_id}")
        except Exception as e:
            logger.error(f"Error initializing BigQueryConnector or BigQueryTool in {name}: {e}")
            self._connector = None
            self._bigquery_tool = None # Ensure tool is also None if connector fails

        try:
            self._schema_agent = SchemaAgent(project_id=self._project_id, name="DataAnalystInternalSchemaAgent")
            logger.info(f"{name} successfully initialized internal SchemaAgent.")
        except Exception as e:
            logger.error(f"Error initializing internal SchemaAgent in {name}: {e}")
            self._schema_agent = None

        self.model = GenerativeModel("gemini-1.0-pro")
        logger.info(f"{name} (DataAnalystAgent) initialized successfully.")

    @property
    def project_id(self) -> str:
        """Get the project ID."""
        return self._project_id

    @property
    def connector(self):
        """Get the BigQuery connector."""
        return self._connector

    @property
    def bigquery_tool(self):
        """Get the BigQuery tool."""
        return self._bigquery_tool

    @property
    def schema_agent(self):
        """Get the schema agent."""
        return self._schema_agent

    def process(self, query: str, dataset_schema: dict, project_id: str, dataset_id: str) -> dict:
        """
        Processes a natural language query, converts it to a SQL query using the provided dataset schema,
        executes it, and returns the results along with the SQL query.
        """
        logger.info(f"{self.name}: Processing query: '{query}' for dataset: {project_id}.{dataset_id}")

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
