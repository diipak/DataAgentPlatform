# agents/data_analyst_agent.py

import os
import logging # Added import
import vertexai

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
        
        # Initialize Vertex AI
        try:
            vertexai.init(project=self._project_id, location="europe-west4")
            logger.info(f"{name} initialized Vertex AI successfully.")
        except Exception as e:
            logger.error(f"Error initializing Vertex AI in {name}: {e}")
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

        try:
            self.model = GenerativeModel("gemini-2.5-flash")
            logger.info(f"{name} initialized Gemini model successfully.")
        except Exception as e:
            logger.warning(f"Error initializing Gemini model in {name}: {e}")
            # Try fallback models
            fallback_models = ["gemini-2.5-flash", "gemini-2.5-pro", "text-bison@001"]
            model_initialized = False
            
            for fallback_model in fallback_models:
                try:
                    self.model = GenerativeModel(fallback_model)
                    logger.info(f"{name} initialized fallback model {fallback_model} successfully.")
                    model_initialized = True
                    break
                except Exception as fallback_error:
                    logger.warning(f"Error initializing fallback model {fallback_model} in {name}: {fallback_error}")
            
            if not model_initialized:
                logger.error(f"All model initialization attempts failed in {name}. Vertex AI may not be enabled.")
                self.model = None
        
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
        if not self.model:
            # Try to handle basic queries without LLM
            sql_query = self._generate_basic_sql(query, formatted_schema_parts, project_id, dataset_id)
            if sql_query:
                return_value['sql_query'] = sql_query
                logger.info(f"Generated basic SQL query: {sql_query}")
            else:
                return_value['error'] = """Language model is not available. This could be because:
• Vertex AI API is not enabled for your project
• Your project doesn't have access to Gemini models
• Authentication issues

To fix this:
1. Enable the Vertex AI API in Google Cloud Console
2. Ensure your service account has 'Vertex AI User' role
3. Try running: gcloud auth application-default login

I can handle basic queries like 'show first 10 rows', 'count records', or 'show columns' without the language model."""
                return return_value
            
        try:
            logger.info("Generating SQL query using LLM...")
            response = self.model.generate_content(prompt)
            # Clean up the response to get only the SQL query
            cleaned_text = response.text.strip()
            # Remove markdown code blocks
            cleaned_text = cleaned_text.replace("```sql", "").replace("```", "")

            # Sometimes the model prefixes with 'bigquery' or 'sql', so we remove it case-insensitively
            if cleaned_text.lower().lstrip().startswith('bigquery'):
                # Find the start of the actual SQL statement (e.g., SELECT)
                select_pos = cleaned_text.lower().find('select')
                if select_pos != -1:
                    cleaned_text = cleaned_text[select_pos:]
            
            # Remove extra whitespace and ensure proper formatting
            sql_query = ' '.join(cleaned_text.split())
            
            # Validate the query starts with a valid SQL keyword
            valid_starts = ['SELECT', 'WITH', 'CREATE', 'INSERT', 'UPDATE', 'DELETE']
            if not any(sql_query.upper().startswith(start) for start in valid_starts):
                # Try to extract SQL from the response
                lines = cleaned_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if any(line.upper().startswith(start) for start in valid_starts):
                        sql_query = line
                        break
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

    def _generate_basic_sql(self, query: str, schema_parts: list, project_id: str, dataset_id: str) -> str:
        """Generate basic SQL queries without using LLM for common patterns."""
        query_lower = query.lower().strip()
        
        # Extract table name from dataset_id (it might be dataset.table format)
        if '.' in dataset_id:
            dataset_name, table_name = dataset_id.split('.', 1)
            full_table_ref = f"`{project_id}.{dataset_name}.{table_name}`"
        else:
            # If no table specified, try to get first table from schema
            if schema_parts:
                first_schema = schema_parts[0]
                if "Table:" in first_schema:
                    table_name = first_schema.split("Table:")[1].split(",")[0].strip()
                    full_table_ref = f"`{project_id}.{dataset_id}.{table_name}`"
                else:
                    return None
            else:
                return None
        
        # Basic query patterns
        if any(phrase in query_lower for phrase in ["first 10 rows", "show me the first 10", "first ten rows"]):
            return f"SELECT * FROM {full_table_ref} LIMIT 10"
        
        elif any(phrase in query_lower for phrase in ["total number of records", "count records", "how many rows"]):
            return f"SELECT COUNT(*) as total_records FROM {full_table_ref}"
        
        elif any(phrase in query_lower for phrase in ["what columns", "show columns", "column names"]):
            # For column info, we need the dataset and table name separately
            if '.' in dataset_id:
                dataset_name, table_name = dataset_id.split('.', 1) 
            else:
                dataset_name = dataset_id
                if schema_parts and "Table:" in schema_parts[0]:
                    table_name = schema_parts[0].split("Table:")[1].split(",")[0].strip()
                else:
                    return None
            return f"SELECT column_name, data_type FROM `{project_id}.{dataset_name}`.INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{table_name}'"
        
        elif any(phrase in query_lower for phrase in ["summary", "describe", "overview"]):
            return f"SELECT * FROM {full_table_ref} LIMIT 5"
        
        else:
            return None
