from typing import Dict, List, Optional
from google.cloud import bigquery

class BigQueryTool:
    """ADK-compatible tool for BigQuery operations."""
    
    def __init__(self, project_id: str):
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id
    
    def get_schema(self, table_name: str) -> Dict:
        """Get the schema of a BigQuery table."""
        try:
            table = self.client.get_table(table_name)
            return {
                'table': table_name,
                'columns': [field.name for field in table.schema],
                'types': [field.field_type for field in table.schema]
            }
        except Exception as e:
            return {
                'error': str(e),
                'table': table_name
            }
    
    def execute_query(self, query: str) -> Dict:
        """Execute a BigQuery query."""
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            return {
                'success': True,
                'results': [dict(row) for row in results]
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def optimize_query(self, query: str) -> Dict:
        """Analyze and optimize a BigQuery query."""
        try:
            # Basic optimization - could be enhanced with more sophisticated analysis
            optimized_query = query
            
            # Add caching hint if appropriate
            if 'SELECT' in query.upper():
                optimized_query = f"/*+ OPTIONS(use_cache=true) */ {query}"
            
            return {
                'optimized_query': optimized_query,
                'estimated_cost': self.estimate_cost(query)
            }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def estimate_cost(self, query: str) -> float:
        """Estimate the cost of a BigQuery query."""
        try:
            query_job = self.client.query(query, dry_run=True)
            return query_job.total_bytes_processed / 1024 / 1024 / 1024  # GB
        except Exception as e:
            return 0.0
