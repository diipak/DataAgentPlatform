"""
Intelligent Analytics Question Generator
Generates context-aware questions based on dataset schema and content.
"""

import pandas as pd
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Default fallback questions when no context is available
DEFAULT_QUESTIONS = [
    "📊 Show me the main trends",
    "📈 What are the key metrics?", 
    "🌍 Summarize the dataset for me",
    "🔍 Find interesting correlations"
]

class IntelligentQuestionGenerator:
    """Generates intelligent, context-aware analytics questions based on dataset characteristics."""
    
    def __init__(self):
        self.time_keywords = ['date', 'time', 'timestamp', 'year', 'month', 'day', 'created', 'updated']
        self.metric_keywords = ['amount', 'count', 'total', 'sum', 'avg', 'revenue', 'sales', 'price', 'cost', 'value']
        self.category_keywords = ['type', 'category', 'group', 'status', 'region', 'department', 'segment']
        
    def generate_intelligent_questions(self, dataset_name: Optional[str] = None, 
                                     schema_info: Optional[Dict[str, Any]] = None,
                                     sample_data: Optional[pd.DataFrame] = None) -> List[str]:
        """
        Generate intelligent questions based on dataset context.
        
        Args:
            dataset_name: Name of the selected dataset
            schema_info: Dictionary containing schema information (columns, types, etc.)
            sample_data: Sample DataFrame for analysis
            
        Returns:
            List of 4 intelligent questions or default questions if no context available
        """
        try:
            if not dataset_name and not schema_info and (sample_data is None or sample_data.empty):
                logger.info("No context available, returning default questions")
                return DEFAULT_QUESTIONS
                
            questions = []
            
            # Analyze schema information if available
            if schema_info and 'columns' in schema_info:
                questions.extend(self._generate_from_schema(schema_info, dataset_name))
            
            # Analyze sample data if available
            if sample_data is not None and not sample_data.empty:
                questions.extend(self._generate_from_sample_data(sample_data, dataset_name))
            
            # If we have questions, return the best 4
            if questions:
                unique_questions = list(dict.fromkeys(questions))  # Remove duplicates while preserving order
                return unique_questions[:4]
            
            # Fallback to default questions
            logger.info("Could not generate intelligent questions, returning defaults")
            return DEFAULT_QUESTIONS
            
        except Exception as e:
            logger.error(f"Error generating intelligent questions: {e}")
            return DEFAULT_QUESTIONS
    
    def _generate_from_schema(self, schema_info: Dict[str, Any], dataset_name: Optional[str]) -> List[str]:
        """Generate questions based on schema information."""
        questions = []
        columns = schema_info.get('columns', [])
        
        if not columns:
            return questions
            
        # Find different types of columns
        time_cols = [col for col in columns if any(keyword in col.lower() for keyword in self.time_keywords)]
        metric_cols = [col for col in columns if any(keyword in col.lower() for keyword in self.metric_keywords)]
        category_cols = [col for col in columns if any(keyword in col.lower() for keyword in self.category_keywords)]
        
        dataset_ref = f"in {dataset_name}" if dataset_name else ""
        
        # Generate time-based questions
        if time_cols:
            time_col = time_cols[0]
            questions.append(f"📈 What's the trend over {time_col} {dataset_ref}?")
            if metric_cols:
                questions.append(f"📊 How does {metric_cols[0]} change over {time_col}?")
        
        # Generate comparison questions
        if category_cols and metric_cols:
            questions.append(f"🔍 Compare {metric_cols[0]} across different {category_cols[0]}")
        
        # Generate summary questions
        if len(columns) > 3:
            questions.append(f"📋 What are the key patterns {dataset_ref}?")
        
        return questions
    
    def _generate_from_sample_data(self, sample_data: pd.DataFrame, dataset_name: Optional[str]) -> List[str]:
        """Generate questions based on actual sample data analysis."""
        questions = []
        
        try:
            numeric_cols = sample_data.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = sample_data.select_dtypes(include=['object', 'category']).columns.tolist()
            datetime_cols = sample_data.select_dtypes(include=['datetime']).columns.tolist()
            
            dataset_ref = f"in {dataset_name}" if dataset_name else ""
            
            # Time series questions
            if datetime_cols:
                if numeric_cols:
                    questions.append(f"📈 Show {numeric_cols[0]} trends over {datetime_cols[0]}")
                questions.append(f"📅 What patterns exist over {datetime_cols[0]} {dataset_ref}?")
            
            # Statistical questions
            if len(numeric_cols) >= 2:
                questions.append(f"🔗 What's the correlation between {numeric_cols[0]} and {numeric_cols[1]}?")
            
            # Category analysis
            if categorical_cols and numeric_cols:
                questions.append(f"📊 Which {categorical_cols[0]} has the highest {numeric_cols[0]}?")
            
            # Distribution questions
            if numeric_cols:
                questions.append(f"📉 What's the distribution of {numeric_cols[0]} {dataset_ref}?")
                
            # Outlier detection
            if len(numeric_cols) > 0:
                questions.append(f"⚠️ Are there any outliers in {numeric_cols[0]} {dataset_ref}?")
            
        except Exception as e:
            logger.error(f"Error analyzing sample data: {e}")
            
        return questions

# Global instance for easy access
question_generator = IntelligentQuestionGenerator()

def get_intelligent_questions(dataset_name: Optional[str] = None, 
                            schema_info: Optional[Dict[str, Any]] = None,
                            sample_data: Optional[pd.DataFrame] = None) -> List[str]:
    """
    Convenience function to get intelligent questions.
    
    Args:
        dataset_name: Name of the selected dataset
        schema_info: Dictionary containing schema information
        sample_data: Sample DataFrame for analysis
        
    Returns:
        List of 4 intelligent questions
    """
    return question_generator.generate_intelligent_questions(dataset_name, schema_info, sample_data)