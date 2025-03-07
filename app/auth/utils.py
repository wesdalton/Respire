"""
Authentication utilities for Burnout Predictor application
"""

import os
import logging
from flask import session as flask_session
from app.database import USE_SUPABASE

logger = logging.getLogger(__name__)

# Import the correct database functions based on configuration
if USE_SUPABASE:
    from app.database.supabase import get_current_user
else:
    # SQLite fallback
    from app.database.sqlite import get_user_by_id

def is_authenticated():
    """Check if the user is authenticated"""
    # Check Supabase session
    try:
        if USE_SUPABASE:
            # Check Supabase auth
            current_user = get_current_user()
            return current_user is not None
        else:
            # Check Flask session for SQLite
            return 'user_id' in flask_session
    except Exception as e:
        logger.error(f"Error checking authentication: {str(e)}")
        return False

def get_user_id():
    """Get the current user ID"""
    # First check Flask session in any case
    user_id = flask_session.get('user_id')
    if user_id:
        logger.debug(f"Found user_id in Flask session: {user_id}")
        return user_id
        
    # Try to get from Supabase auth if using Supabase
    if USE_SUPABASE:
        try:
            current_user = get_current_user()
            if current_user and current_user.user:
                logger.debug(f"Found user from Supabase auth: {current_user.user.id}")
                return current_user.user.id
        except Exception as e:
            logger.error(f"Error getting user from Supabase: {str(e)}")
            
    # Fall back to admin user
    admin_id = os.getenv("SUPABASE_USER_ID")
    if admin_id:
        logger.debug(f"Using admin ID from env: {admin_id}")
        return admin_id
            
    # Last resort - this should not happen in production
    logger.warning("No user ID found, using default")
    return "default"