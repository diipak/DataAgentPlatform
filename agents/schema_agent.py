import os
import logging
from typing import List, Dict, Optional, Any

from google.adk.agents import Agent
from connectors.bigquery_connector import BigQueryConnector

logger = logging.getLogger(__name__)

class SchemaAgent(Agent):
    """Agent responsible for understanding and retrieving BigQuery database schemas."""

    def __init__(self, project_id: Optional[str] = None):
        super().__init__()
        if project_id is None:
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

        if not project_id:
            logger.error("GOOGLE_CLOUD_PROJECT environment variable not set and no project_id provided.")
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set and no project_id provided.")

        try:
            self.connector = BigQueryConnector(project_id=project_id)
            logger.info(f"SchemaAgent initialized with project_id: {project_id}")
        except Exception as e:
            logger.error(f"Error initializing BigQueryConnector in SchemaAgent: {e}")
            # Depending on desired behavior, either raise e or handle it
            # For now, let's make the agent still runnable but without a connector
            self.connector = None
            # raise e # Or re-raise if the connector is critical for __init__

    def get_available_datasets(self) -> List[str]:
        """Retrieves a list of available dataset IDs from BigQuery."""
        if not self.connector:
            logger.error("BigQueryConnector not initialized in SchemaAgent.")
            return []
        try:
            datasets = self.connector.list_datasets()
            return datasets
        except Exception as e:
            logger.error(f"Error retrieving datasets: {e}")
            return []

    def get_tables_in_dataset(self, dataset_id: str) -> List[str]:
        """Retrieves a list of table IDs within a specified dataset."""
        if not self.connector:
            logger.error("BigQueryConnector not initialized in SchemaAgent.")
            return []
        if not dataset_id:
            logger.warning("dataset_id cannot be empty.")
            return []
        try:
            tables = self.connector.list_tables(dataset_id=dataset_id)
            return tables
        except Exception as e:
            logger.error(f"Error retrieving tables for dataset {dataset_id}: {e}")
            return []

    def get_schema_for_table(self, dataset_id: str, table_id: str) -> Optional[Dict[str, List[Dict[str, str]]]]:
        """Retrieves the schema for a specific table in a dataset."""
        if not self.connector:
            logger.error("BigQueryConnector not initialized in SchemaAgent.")
            return None
        if not dataset_id or not table_id:
            logger.warning("dataset_id and table_id cannot be empty.")
            return None
        try:
            schema = self.connector.get_table_schema(dataset_id=dataset_id, table_id=table_id)
            return schema
        except Exception as e:
            logger.error(f"Error retrieving schema for table {dataset_id}.{table_id}: {e}")
            return None

    def get_full_dataset_schema(self, dataset_id: str) -> Dict[str, Any]:
        """
        Retrieves the schemas for all tables in a dataset and compiles them.
        Returns a dictionary where keys are table IDs and values are their schemas.
        e.g. {'table_one': {'columns': [...]}, 'table_two': {'columns': [...]}}
        """
        if not self.connector:
            logger.error("BigQueryConnector not initialized in SchemaAgent.")
            return {}
        if not dataset_id:
            logger.warning("dataset_id cannot be empty.")
            return {}

        full_schema = {}
        table_ids = self.get_tables_in_dataset(dataset_id)
        if not table_ids:
            logger.warning(f"No tables found or error retrieving tables for dataset {dataset_id}.")
            return {}

        for table_id in table_ids:
            schema = self.get_schema_for_table(dataset_id, table_id)
            if schema:
                full_schema[table_id] = schema
            else:
                logger.warning(f"Could not retrieve schema for table {table_id} in dataset {dataset_id}.")
                full_schema[table_id] = {'error': f'Could not retrieve schema for table {table_id}'} # Or skip

        return full_schema

# Example usage (optional, for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Ensure GOOGLE_CLOUD_PROJECT is set as an environment variable
    # For example: export GOOGLE_CLOUD_PROJECT='your-gcp-project-id'
    # Or pass it directly: agent = SchemaAgent(project_id='your-gcp-project-id')

    gcp_project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not gcp_project_id:
        print("Please set the GOOGLE_CLOUD_PROJECT environment variable to run this example.")
    else:
        agent = SchemaAgent()
        if agent.connector: # Check if connector was initialized
            print(f"SchemaAgent created for project: {agent.connector.project_id}")

            datasets = agent.get_available_datasets()
            print(f"Available datasets: {datasets}")

            if datasets:
                # Example: use the first dataset found
                selected_dataset = datasets[0]
                print(f"--- Tables in dataset: {selected_dataset} ---")
                tables = agent.get_tables_in_dataset(selected_dataset)
                print(tables)

                if tables:
                    # Example: get schema for the first table
                    selected_table = tables[0]
                    print(f"--- Schema for table: {selected_dataset}.{selected_table} ---")
                    table_schema = agent.get_schema_for_table(selected_dataset, selected_table)
                    print(table_schema)

                    print(f"--- Full schema for dataset: {selected_dataset} ---")
                    dataset_schema = agent.get_full_dataset_schema(selected_dataset)
                    import json
                    print(json.dumps(dataset_schema, indent=2))
        else:
            print("SchemaAgent's BigQueryConnector failed to initialize. Check logs and GCP setup.")
