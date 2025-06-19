import logging
import pandas as pd
from typing import Dict, Any, List, Optional

from google.adk.agents import Agent
import plotly.express as px
import plotly.io as pio

logger = logging.getLogger(__name__)

class VisualizationAgent(Agent):
    """Agent responsible for generating visualizations and insights from data."""

    def __init__(self):
        super().__init__()
        logger.info("VisualizationAgent initialized.")

    def generate_visualizations(self, data_df: pd.DataFrame, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates visualizations and textual insights from a pandas DataFrame.

        Args:
            data_df: The pandas DataFrame containing the data to visualize.
            query: The original natural language query that produced this data (optional).

        Returns:
            A dictionary containing:
                'charts': A list of Plotly figure objects (or their JSON representations).
                'insights_text': A string containing any generated textual insights.
        """
        charts_json = []
        insights_text = ""

        if data_df.empty:
            insights_text = "The dataset is empty, no visualizations can be generated."
            return {"charts": charts_json, "insights_text": insights_text}

        # Attempt to generate some common chart types
        # This logic can be significantly expanded based on data characteristics.

        try:
            # Insight: Basic DataFrame description
            insights_text += "Data Snapshot:\n" + data_df.head().to_string() + "\n\n"
            insights_text += "Basic Statistics:\n" + data_df.describe(include='all').to_string() + "\n\n"

            # 1. Try a Bar Chart if suitable columns exist
            # Heuristic: first non-numeric column as x, first numeric as y
            numeric_cols = data_df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = data_df.select_dtypes(include=['object', 'category']).columns.tolist()

            if categorical_cols and numeric_cols:
                try:
                    x_col_bar = categorical_cols[0]
                    y_col_bar = numeric_cols[0]
                    logger.info(f"Attempting to generate a bar chart with x='{x_col_bar}', y='{y_col_bar}'.")
                    fig_bar = px.bar(data_df.head(20), x=x_col_bar, y=y_col_bar,
                                     title=f"Bar Chart: {y_col_bar} by {x_col_bar} (Top 20 rows)")
                    charts_json.append(pio.to_json(fig_bar))
                    insights_text += f"Generated a bar chart showing '{y_col_bar}' by '{x_col_bar}'.\n"
                except Exception as e:
                    logger.warning(f"Could not generate bar chart: {e}")
                    insights_text += f"Could not generate a default bar chart: {e}\n"

            # 2. Try a Histogram for the first numeric column
            if numeric_cols:
                try:
                    hist_col = numeric_cols[0]
                    logger.info(f"Attempting to generate a histogram for '{hist_col}'.")
                    fig_hist = px.histogram(data_df, x=hist_col, title=f"Histogram for {hist_col}")
                    charts_json.append(pio.to_json(fig_hist))
                    insights_text += f"Generated a histogram for '{hist_col}'.\n"
                except Exception as e:
                    logger.warning(f"Could not generate histogram: {e}")
                    insights_text += f"Could not generate a default histogram: {e}\n"

            # 3. Try a Scatter Plot if at least two numeric columns exist
            if len(numeric_cols) >= 2:
                try:
                    x_col_scatter = numeric_cols[0]
                    y_col_scatter = numeric_cols[1]
                    logger.info(f"Attempting to generate a scatter plot with x='{x_col_scatter}', y='{y_col_scatter}'.")
                    # Use a sample for potentially large datasets in scatter plots
                    sample_df = data_df.sample(n=min(1000, len(data_df)))
                    fig_scatter = px.scatter(sample_df, x=x_col_scatter, y=y_col_scatter,
                                             title=f"Scatter Plot: {y_col_scatter} vs {x_col_scatter} (sample)")
                    charts_json.append(pio.to_json(fig_scatter))
                    insights_text += f"Generated a scatter plot for '{y_col_scatter}' vs '{x_col_scatter}'.\n"
                except Exception as e:
                    logger.warning(f"Could not generate scatter plot: {e}")
                    insights_text += f"Could not generate a default scatter plot: {e}\n"

            if not charts_json:
                insights_text += "Could not automatically determine suitable chart types for the given data."

        except Exception as e:
            logger.error(f"Error during visualization generation: {e}")
            insights_text += f"An error occurred during visualization: {e}"
            # Fallback or ensure partial results are returned
            return {"charts": charts_json, "insights_text": insights_text}

        return {"charts": charts_json, "insights_text": insights_text}

# Example Usage (optional, for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    agent = VisualizationAgent()

    # Create sample data
    sample_data = {
        'Category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'C', 'B', 'A'],
        'Value1': [10, 15, 12, 8, 18, 9, 10, 12, 16, 11],
        'Value2': [20, 25, 22, 18, 28, 19, 20, 22, 26, 21],
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                 '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10'])
    }
    df = pd.DataFrame(sample_data)

    results = agent.generate_visualizations(df.copy(), query="Show me category values") # Use .copy() if df is modified
    print("--- Generated Charts (JSON) ---")
    for i, chart_json_str in enumerate(results['charts']):
        # chart_fig = pio.from_json(chart_json_str) # To convert back to fig if needed
        # chart_fig.show() # This would open a browser window for each chart
        print(f"Chart {i+1} JSON (first 200 chars): {chart_json_str[:200]}...")
        # In a Dash app, you'd pass this JSON string to dcc.Graph(figure=json.loads(chart_json_str))

    print("\n--- Generated Insights ---")
    print(results['insights_text'])

    # Test with empty DataFrame
    empty_df = pd.DataFrame()
    results_empty = agent.generate_visualizations(empty_df)
    print("\n--- Results for Empty DataFrame ---")
    print(results_empty['insights_text'])
    print(results_empty['charts'])
