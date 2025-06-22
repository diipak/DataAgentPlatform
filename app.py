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
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap',
    ],
    suppress_callback_exceptions=True,
    assets_folder='assets',
    assets_ignore=r'.*\.(js|jsx|ts|tsx|py|pyc)$'
)

# Include custom CSS files in the correct order
import time
cache_buster = str(int(time.time()))
app.css.config.serve_locally = True
app.css.append_css({
    'external_url': [
        f'/assets/styles/base.css?v={cache_buster}',
        f'/assets/styles/utilities.css?v={cache_buster}',
        f'/assets/styles/theme.css?v={cache_buster}',
        f'/assets/styles/layout.css?v={cache_buster}',
        f'/assets/styles/components.css?v={cache_buster}',
        f'/assets/styles/visualizations.css?v={cache_buster}',
        f'/assets/styles/chatbot-layout.css?v={cache_buster}',
        f'/assets/styles/print.css?v={cache_buster}'
    ]
})

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
    app.run_server(debug=True, port=8051)
