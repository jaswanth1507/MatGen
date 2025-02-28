"""
Flask application factory that initializes and configures the app.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from app.config import config

def create_app(config_name):
    """
    Create and configure the Flask application.
    
    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')
        
    Returns:
        Flask: Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__, static_folder='static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Configure logging
    setup_logging(app)
    
    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Print initialization info
    app.logger.info(f"Initialized app with {config_name} configuration")
    app.logger.info(f"Model directory: {app.config['MODEL_DIR']}")
    
    return app

def setup_logging(app):
    """Configure application logging"""
    log_level = app.config.get('LOG_LEVEL', logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Configure file handler if log file specified
    log_file = app.config.get('LOG_FILE')
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logging.getLogger().addHandler(file_handler)