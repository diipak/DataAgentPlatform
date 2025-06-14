from google.cloud import bigquery
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class BigQueryTool:
    """A tool for interacting with Google BigQuery."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = bigquery.Client(project=project_id)

    def get_schema(self, table_id: str) -> dict:
        """
        Retrieves the schema of a BigQuery table.

        Args:
            table_id: The ID of the table in the format 'project.dataset.table'.

        Returns:
            A dictionary containing the table schema or an error message.
        """
        try:
            logger.info(f"Retrieving schema for table: {table_id}")
            table = self.client.get_table(table_id)
            schema = [{'name': field.name, 'type': field.field_type} for field in table.schema]
            logger.info(f"Successfully retrieved schema for table: {table_id}")
            return {'columns': schema}
        except Exception as e:
            logger.error(f"Failed to retrieve schema for {table_id}: {e}")
            return {'error': str(e)}

    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Executes a SQL query on BigQuery and returns the result as a DataFrame.

        Args:
            query: The SQL query to execute.

        Returns:
            A pandas DataFrame containing the query results.
        
        Raises:
            Exception: If the query fails to execute.
        """
        try:
            logger.info(f"Executing BigQuery query: {query}")
            query_job = self.client.query(query)
            results = query_job.result()
            df = results.to_dataframe()
            logger.info(f"Query returned {len(df)} rows.")
            return df
        except Exception as e:
            logger.error(f"Error executing BigQuery query: {e}")
            raise
