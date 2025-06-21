import logging
from google.cloud import bigquery
from interfaces.database_interface import DatabaseConnectorInterface
import pandas as pd
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class BigQueryConnector(DatabaseConnectorInterface):
    """Connector for Google BigQuery."""
    
    def __init__(self, project_id: str):
        self.client = None
        self.project_id = project_id
        self.connect()
    
    def connect(self) -> None:
        """Connect to BigQuery."""
        try:
            self.client = bigquery.Client(project=self.project_id)
            logger.info(f"Connected to BigQuery project: {self.project_id}")
        except Exception as e:
            logger.error(f"Error connecting to BigQuery: {str(e)}")
            raise

    def list_datasets(self) -> List[str]:
        """Lists all datasets in the project."""
        try:
            datasets = self.client.list_datasets()
            dataset_ids = [dataset.dataset_id for dataset in datasets]
            logger.info(f"Successfully listed datasets: {dataset_ids}")
            return dataset_ids
        except Exception as e:
            logger.error(f"Error listing datasets: {str(e)}")
            return []

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame."""
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            return results.to_dataframe()
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def list_tables(self, dataset_id: str) -> List[str]:
        """Lists all tables in a given dataset."""
        try:
            tables = self.client.list_tables(dataset_id)
            table_ids = [table.table_id for table in tables]
            logger.info(f"Successfully listed tables in dataset {dataset_id}: {table_ids}")
            return table_ids
        except Exception as e:
            logger.error(f"Error listing tables in dataset {dataset_id}: {str(e)}")
            return []

    def get_table_schema(self, dataset_id: str, table_id: str) -> Optional[Dict[str, List[Dict[str, str]]]]:
        """Retrieves the schema for a specific table."""
        try:
            table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
            table = self.client.get_table(table_ref)
            schema_list = [{'name': field.name, 'type': field.field_type} for field in table.schema]
            logger.info(f"Successfully retrieved schema for table {table_ref}")
            return {'columns': schema_list}
        except Exception as e:
            logger.error(f"Error getting schema for table {table_ref}: {str(e)}")
            return None

    def get_table_info(self) -> Dict[str, List[str]]:
        """Get information about tables in the database, organized by dataset."""
        try:
            datasets = self.list_datasets()
            table_info = {}
            for dataset_id in datasets:
                table_info[dataset_id] = self.list_tables(dataset_id)
            logger.info("Successfully retrieved table info for all datasets.")
            return table_info
        except Exception as e:
            logger.error(f"Error getting table info: {str(e)}")
            return {}

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
