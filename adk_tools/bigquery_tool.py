import pandas as pd
import logging
from typing import Dict, List, Union # Added Union for type hinting
from connectors.bigquery_connector import BigQueryConnector # Added import

logger = logging.getLogger(__name__)

class BigQueryTool:
    """A tool for interacting with Google BigQuery, using a BigQueryConnector."""

    def __init__(self, connector: BigQueryConnector): # Modified parameter
        self.connector = connector # Store the connector instance
        logger.info(f"BigQueryTool initialized with connector for project: {self.connector.project_id}")

    def get_schema(self, table_id: str) -> Dict[str, Union[List[Dict[str, str]], str]]: # Modified return type hint
        """
        Retrieves the schema of a BigQuery table using the connector.

        Args:
            table_id: The ID of the table in the format 'project.dataset.table'.

        Returns:
            A dictionary containing the table schema {'columns': [...]} or an error message {'error': ...}.
        """
        try:
            logger.info(f"Attempting to retrieve schema for table: {table_id} using connector.")

            # Parse table_id
            parts = table_id.split('.')
            if len(parts) != 3:
                logger.error(f"Invalid table_id format: {table_id}. Expected 'project.dataset.table'.")
                return {'error': "Invalid table_id format. Expected 'project.dataset.table'."}

            parsed_project_id, parsed_dataset_id, parsed_table_name = parts

            # Validate project_id
            if parsed_project_id != self.connector.project_id:
                logger.error(f"Mismatched project_id: Tool configured for '{self.connector.project_id}', but got table_id for '{parsed_project_id}'.")
                return {'error': f"Mismatched project_id: Connector is for '{self.connector.project_id}', table requested for '{parsed_project_id}'."}

            schema_result = self.connector.get_table_schema(parsed_dataset_id, parsed_table_name)

            if schema_result:
                logger.info(f"Successfully retrieved schema for table: {table_id}")
                return schema_result  # This is already in the format {'columns': [...]}
            else:
                logger.error(f"Failed to retrieve schema for {table_id} using connector (connector returned None).")
                return {'error': f"Failed to retrieve schema for {table_id} (connector returned None or error)."}

        except Exception as e:
            logger.error(f"Exception while retrieving schema for {table_id}: {e}")
            return {'error': str(e)}

    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Executes a SQL query on BigQuery using the connector and returns the result as a DataFrame.

        Args:
            query: The SQL query to execute.

        Returns:
            A pandas DataFrame containing the query results.
        
        Raises:
            Exception: If the query fails to execute (propagated from connector).
        """
        try:
            logger.info(f"Executing BigQuery query via connector: {query}")
            # The connector's execute_query method is expected to return a DataFrame or raise an exception.
            df = self.connector.execute_query(query)
            logger.info(f"Query executed via connector, returned {len(df) if df is not None else 'None'} rows.")
            return df
        except Exception as e:
            logger.error(f"Error executing BigQuery query via connector: {e}")
            raise
