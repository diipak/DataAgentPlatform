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
app.css.config.serve_locally = True
app.css.append_css({
    'external_url': [
        '/assets/styles/base.css',
        '/assets/styles/utilities.css',
        '/assets/styles/theme.css',
        '/assets/styles/layout.css',
        '/assets/styles/components.css',
        '/assets/styles/visualizations.css',
        '/assets/styles/chatbot-layout.css',
        '/assets/styles/print.css'
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
