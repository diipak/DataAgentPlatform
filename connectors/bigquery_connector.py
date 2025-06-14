from google.cloud import bigquery
from interfaces.database_interface import DatabaseConnectorInterface
import pandas as pd
from typing import Dict, List, Optional

class BigQueryConnector(DatabaseConnectorInterface):
    """Connector for Google BigQuery."""
    
    def __init__(self, project_id: str):
        self.client = None
        self.project_id = project_id
    
    def connect(self) -> None:
        """Connect to BigQuery."""
        try:
            self.client = bigquery.Client(project=self.project_id)
            logger.info(f"Connected to BigQuery project: {self.project_id}")
        except Exception as e:
            logger.error(f"Error connecting to BigQuery: {str(e)}")
            raise
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame."""
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            return results.to_dataframe()
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    def get_table_info(self) -> Dict[str, List[str]]:
        """Get information about tables in the dataset."""
        try:
            tables = self.client.list_tables()
            table_info = {}
            for table in tables:
                schema = self.client.get_table(table).schema
                table_info[table.table_id] = [field.name for field in schema]
            return table_info
        except Exception as e:
            logger.error(f"Error getting table info: {str(e)}")
            raise
    
    def get_row_counts(self) -> Dict[str, int]:
        """Get the number of rows in each table."""
        try:
            tables = self.client.list_tables()
            counts = {}
            for table in tables:
                query = f"SELECT COUNT(*) as count FROM `{table.project}.{table.dataset_id}.{table.table_id}`"
                result = self.execute_query(query)
                counts[table.table_id] = result.iloc[0]['count']
            return counts
        except Exception as e:
            logger.error(f"Error getting row counts: {str(e)}")
            raise
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get sample data from a table."""
        try:
            query = f"SELECT * FROM `{self.project_id}.{table_name}` LIMIT {limit}"
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"Error getting sample data: {str(e)}")
            raise
