"""
Burnout Predictor: A web application for tracking and predicting burnout risk.
Uses WHOOP health data and AI-powered insights to help users monitor their well-being.
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

# Logger configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configuration
def create_app(test_config=None):
    """Application factory function to create and configure the app."""
    # Load environment variables
    load_dotenv(override=True)
    
    # Create Flask app
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # App configuration
    app.config.update(
        SECRET_KEY=os.getenv('FLASK_SECRET_KEY', os.urandom(24)),
        SESSION_TYPE='filesystem',
        WHOOP_CLIENT_ID=os.getenv('WHOOP_CLIENT_ID', ''),
        WHOOP_CLIENT_SECRET=os.getenv('WHOOP_CLIENT_SECRET', ''),
        OPENAI_API_KEY=os.getenv('OPENAI_API_KEY', ''),
        OPENAI_MODEL=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        SUPABASE_URL=os.getenv('SUPABASE_URL', ''),
        SUPABASE_KEY=os.getenv('SUPABASE_KEY', ''),
        SUPABASE_SERVICE_KEY=os.getenv('SUPABASE_SERVICE_KEY', ''),
        SUPABASE_USER_ID=os.getenv('SUPABASE_USER_ID', ''),
        REDIRECT_URI=os.getenv('REDIRECT_URI', 'http://localhost:3000'),
        ENV=os.getenv('FLASK_ENV', 'development')
    )
    
    # Initialize database
    from app.database import init_database
    init_database(app)
    
    # Register blueprints
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.core import core_bp
    app.register_blueprint(core_bp)
    
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Initialize Supabase tables if in development
    if app.config['ENV'] == 'development':
        try:
            from app.database.supabase import init_supabase_tables
            init_supabase_tables()
            logger.info("Supabase tables initialized")
        except Exception as e:
            logger.error(f"Error initializing Supabase tables: {str(e)}")
    
    # Set up scheduler for daily data fetching
    scheduler = BackgroundScheduler()
    from app.services.whoop_service import fetch_and_store_whoop_data
    
    # Schedule job to run daily at midnight
    scheduler.add_job(func=fetch_and_store_whoop_data, trigger="cron", hour=0, minute=5)
    scheduler.start()
    
    return app