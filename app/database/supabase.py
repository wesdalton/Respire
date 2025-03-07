"""
Supabase database client and operations for Burnout Predictor
"""

import os
import json
import logging
from datetime import datetime
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Global Supabase client instance
supabase = None

def init_supabase_client(url=None, key=None, service_key=None):
    """Initialize the Supabase client"""
    global supabase
    
    # Use provided values or fall back to environment variables
    url = url or os.getenv("SUPABASE_URL")
    key = key or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        logger.error("Supabase URL or API key not provided")
        raise ValueError("Supabase URL and API key are required")
    
    # Create Supabase client
    try:
        supabase = create_client(url, key)
        logger.info("Supabase client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}")
        raise

def init_supabase_tables():
    """Initialize required tables in Supabase if they don't exist"""
    global supabase
    
    try:
        # Check if client exists
        if not supabase:
            # Initialize client using env vars
            init_supabase_client()
        
        # Create whoop_tokens table (if needed)
        logger.info("Creating whoop_tokens table...")
        supabase.table("whoop_tokens").insert({
            "id": 1,  # Will fail if table exists, that's fine
            "user_id": "test",
            "access_token": "test",
            "refresh_token": "test",
            "created_at": datetime.now().isoformat()
        }).execute()
        
        # Create daily_metrics table (if needed)
        logger.info("Creating daily_metrics table...")
        supabase.table("daily_metrics").insert({
            "id": 1,  # Will fail if table exists, that's fine
            "user_id": "test",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "recovery_score": 0,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        # Create user_settings table (if needed)
        logger.info("Creating user_settings table...")
        supabase.table("user_settings").insert({
            "id": 1,  # Will fail if table exists, that's fine
            "user_id": "test",
            "settings_key": "test",
            "settings_value": "test",
            "created_at": datetime.now().isoformat()
        }).execute()
        
        logger.info("Supabase tables initialized")
    except Exception as e:
        logger.error(f"Error initializing Supabase tables: {str(e)}")
        # Not raising exception as this is non-critical and will fail on existing tables

# User Authentication Functions
def sign_up(email, password):
    """Register a new user"""
    return supabase.auth.sign_up({"email": email, "password": password})

def sign_in(email, password):
    """Sign in existing user"""
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def sign_out(session):
    """Sign out user"""
    return supabase.auth.sign_out()

def get_current_user():
    """Get current authenticated user"""
    try:
        return supabase.auth.get_user()
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        return None

# Whoop Token Functions
def save_whoop_token(user_id, token_data):
    """Save WHOOP API token to Supabase"""
    # Check if token already exists
    existing = supabase.table("whoop_tokens").select("*").eq("user_id", user_id).execute()
    
    # Prepare token data
    token_info = {
        "user_id": user_id,
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token", None),
        "token_type": token_data.get("token_type", "Bearer"),
        "expires_in": token_data.get("expires_in", 0),
        "updated_at": datetime.now().isoformat()
    }
    
    # Update or insert token
    if existing.data and len(existing.data) > 0:
        response = supabase.table("whoop_tokens").update(token_info).eq("user_id", user_id).execute()
    else:
        token_info["created_at"] = datetime.now().isoformat()
        response = supabase.table("whoop_tokens").insert(token_info).execute()
    
    return response.data

def get_whoop_token(user_id):
    """Get WHOOP API token from Supabase"""
    response = supabase.table("whoop_tokens").select("*").eq("user_id", user_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

# Metrics Functions
def save_daily_metrics(user_id, metrics_data, mood_data=None):
    """Save daily metrics to Supabase
    
    Args:
        user_id: User ID
        metrics_data: Dictionary with metrics data
        mood_data: Optional dictionary with mood rating and notes
    """
    # Ensure metrics_data has a date
    if not metrics_data.get("date"):
        metrics_data["date"] = datetime.now().strftime("%Y-%m-%d")
    
    # If mood_data provided, merge it with metrics_data
    if mood_data:
        metrics_data.update(mood_data)
    
    # Add user_id to metrics
    metrics_data["user_id"] = user_id
    metrics_data["updated_at"] = datetime.now().isoformat()
    
    # Check if metrics exist for this date
    existing = supabase.table("daily_metrics").select("*").eq("user_id", user_id).eq("date", metrics_data["date"]).execute()
    
    if existing.data and len(existing.data) > 0:
        # Update existing record
        response = supabase.table("daily_metrics").update(metrics_data).eq("user_id", user_id).eq("date", metrics_data["date"]).execute()
    else:
        # Insert new record
        metrics_data["created_at"] = datetime.now().isoformat()
        response = supabase.table("daily_metrics").insert(metrics_data).execute()
    
    return response.data

def get_daily_metrics(user_id, date=None):
    """Get daily metrics from Supabase
    
    Args:
        user_id: User ID
        date: Optional specific date
        
    Returns:
        List of metrics dictionaries
    """
    query = supabase.table("daily_metrics").select("*").eq("user_id", user_id)
    
    if date:
        # Get specific date
        query = query.eq("date", date)
    else:
        # Get all dates, ordered by date descending
        query = query.order("date", desc=True)
    
    response = query.execute()
    return response.data if response.data else []

def get_metrics_range(user_id, start_date, end_date):
    """Get metrics for a date range
    
    Args:
        user_id: User ID
        start_date: Start date (inclusive)
        end_date: End date (exclusive)
        
    Returns:
        List of metrics dictionaries
    """
    response = supabase.table("daily_metrics").select("*").eq("user_id", user_id).gte("date", start_date).lt("date", end_date).order("date", desc=True).execute()
    return response.data if response.data else []

def delete_mood_data(user_id, date):
    """Delete mood data for a specific date
    
    Args:
        user_id: User ID
        date: Date string in format 'YYYY-MM-DD'
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Direct PATCH request to set mood_rating and notes to null
        response = supabase.table("daily_metrics").update({
            "mood_rating": None,
            "notes": None,
            "updated_at": datetime.now().isoformat()
        }).eq("user_id", user_id).eq("date", date).execute()
        
        if response.data and len(response.data) > 0:
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting mood data: {str(e)}")
        return False

# User Settings Functions
def save_user_setting(user_id, key, value):
    """Save a user setting
    
    Args:
        user_id: User ID
        key: Setting key
        value: Setting value (can be any JSON-serializable value)
    """
    # Check if setting exists
    existing = supabase.table("user_settings").select("*").eq("user_id", user_id).eq("settings_key", key).execute()
    
    setting_data = {
        "user_id": user_id,
        "settings_key": key,
        "settings_value": json.dumps(value) if not isinstance(value, str) else value,
        "updated_at": datetime.now().isoformat()
    }
    
    if existing.data and len(existing.data) > 0:
        # Update
        response = supabase.table("user_settings").update(setting_data).eq("user_id", user_id).eq("settings_key", key).execute()
    else:
        # Insert
        setting_data["created_at"] = datetime.now().isoformat()
        response = supabase.table("user_settings").insert(setting_data).execute()
    
    return response.data

def get_user_setting(user_id, key, default=None):
    """Get a user setting
    
    Args:
        user_id: User ID
        key: Setting key
        default: Default value if setting not found
        
    Returns:
        Setting value or default
    """
    response = supabase.table("user_settings").select("*").eq("user_id", user_id).eq("settings_key", key).execute()
    
    if response.data and len(response.data) > 0:
        value = response.data[0].get("settings_value")
        try:
            # Try to parse as JSON
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # Return as string
            return value
    
    return default