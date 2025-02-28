#!/usr/bin/env python3
"""
Entry point for the Material Generator API server.
Loads configuration, initializes Flask app, and runs the server.
"""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Configure app based on environment variables
config_name = os.getenv('FLASK_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    # Print server information
    print(f"Starting Material Generator API server on port {port}")
    print(f"Debug mode: {debug}")
    print(f"API URL: http://localhost:{port}/api/health")
    
    # Run the server
    app.run(host='0.0.0.0', port=port, debug=debug)