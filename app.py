import os
import dash
import dash_bootstrap_components as dbc
from dash import html
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

# Import components
from layouts.main_layout import create_layout
from callbacks.main_callbacks import register_callbacks

# Set app layout
app.layout = create_layout()

# Register callbacks
register_callbacks(app)
server = app.server

# --- Run the App ---
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
