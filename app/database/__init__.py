"""
Database package for Burnout Predictor
Handles Supabase and SQLite database connections and operations
"""

import os
import logging

logger = logging.getLogger(__name__)

# Default to Supabase
USE_SUPABASE = True

def init_database(app):
    """Initialize database connection based on configuration"""
    global USE_SUPABASE
    
    # Load database configuration from app
    if not app.config.get('SUPABASE_URL') or not app.config.get('SUPABASE_KEY'):
        logger.warning("Supabase credentials not found, falling back to SQLite")
        USE_SUPABASE = False
    else:
        logger.info("Using Supabase for database operations")
        USE_SUPABASE = True
        
    # Initialize the appropriate database
    if USE_SUPABASE:
        from .supabase import init_supabase_client
        init_supabase_client(
            app.config.get('SUPABASE_URL'),
            app.config.get('SUPABASE_KEY'),
            app.config.get('SUPABASE_SERVICE_KEY')
        )
    else:
        # SQLite fallback
        from .sqlite import init_sqlite
        init_sqlite(app)

# Export database functions based on backend
if USE_SUPABASE:
    from .supabase import (
        # Auth functions
        sign_up, sign_in, sign_out, get_current_user,
        # Whoop token functions
        save_whoop_token, get_whoop_token,
        # Metrics functions
        save_daily_metrics, get_daily_metrics, get_metrics_range, delete_mood_data,
        # Settings functions
        save_user_setting, get_user_setting
    )
else:
    from .sqlite import (
        # Auth functions
        create_user as sign_up, get_user_by_email, get_user_by_id,
        # Whoop token functions
        save_user_token as save_whoop_token, get_user_token as get_whoop_token,
        # Metrics functions
        add_or_update_daily_metrics as save_daily_metrics, 
        get_all_metrics as get_daily_metrics,
        get_metrics_date_range as get_metrics_range,
        delete_mood as delete_mood_data,
        # Settings functions
        save_setting as save_user_setting, get_setting as get_user_setting
    )