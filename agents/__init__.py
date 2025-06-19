# agents/__init__.py
from .data_analyst_agent import DataAnalystAgent
from .schema_agent import SchemaAgent
from .visualization_agent import VisualizationAgent # Add this line

__all__ = [
    "DataAnalystAgent",
    "SchemaAgent",
    "VisualizationAgent" # Add this agent to the list
]
