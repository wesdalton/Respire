#!/usr/bin/env python3
"""
Main entry point for the Burnout Predictor application.
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Set Flask environment based on environment variable
    is_production = os.getenv("FLASK_ENV") == "production"
    
    # Run the app with appropriate settings
    if is_production:
        # Production settings - safer defaults
        app.logger.info("Starting app in production mode")
        app.run(debug=False, host='0.0.0.0', port=int(os.getenv("PORT", 3000)))
    else:
        # Development settings
        app.logger.info("Starting app in development mode")
        app.run(debug=True, host='127.0.0.1', port=3000)