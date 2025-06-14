from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd

class DatabaseConnectorInterface(ABC):
    """Abstract base class for database connectors."""
    
    @abstractmethod
    def connect(self) -> None:
        """Connect to the database."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame."""
        pass
    
    @abstractmethod
    def get_table_info(self) -> Dict[str, List[str]]:
        """Get information about tables in the database."""
        pass
    
    @abstractmethod
    def get_row_counts(self) -> Dict[str, int]:
        """Get the number of rows in each table."""
        pass
    
    @abstractmethod
    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get sample data from a table."""
        pass
