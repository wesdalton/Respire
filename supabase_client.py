import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")  # For admin operations

supabase: Client = create_client(supabase_url, supabase_key)

def get_service_client() -> Client:
    """Get a Supabase client with service role permissions"""
    return create_client(supabase_url, supabase_service_key)

# User Authentication Functions
def sign_up(email, password, user_metadata=None):
    """Register a new user with Supabase Auth"""
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": user_metadata or {}
            }
        })
        return response
    except Exception as e:
        print(f"Error signing up user: {str(e)}")
        raise

def sign_in(email, password):
    """Sign in a user with email and password"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        print(f"Error signing in user: {str(e)}")
        raise

def sign_out(session):
    """Sign out the current user"""
    try:
        supabase.auth.sign_out()
        return True
    except Exception as e:
        print(f"Error signing out: {str(e)}")
        return False

def get_current_user(session=None):
    """Get the current authenticated user"""
    try:
        user = supabase.auth.get_user()
        return user
    except Exception as e:
        print(f"Error getting current user: {str(e)}")
        return None

# Whoop Token Storage Functions
def save_whoop_token(user_id, token_data):
    """Save or update Whoop token for a user"""
    try:
        # Calculate expiry datetime
        expires_in = token_data.get("expires_in", 0)
        token_expiry = None
        
        if expires_in:
            token_expiry = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
        
        # Create token object
        token_object = {
            "user_id": user_id,
            "access_token": token_data.get("access_token", ""),
            "refresh_token": token_data.get("refresh_token", ""),
            "token_expiry": token_expiry,
            "updated_at": datetime.now().isoformat()
        }
        
        # Check if token already exists for this user
        existing = supabase.table("whoop_tokens").select("*").eq("user_id", user_id).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update existing token
            response = supabase.table("whoop_tokens").update(token_object).eq("user_id", user_id).execute()
        else:
            # Insert new token
            response = supabase.table("whoop_tokens").insert(token_object).execute()
            
        return token_object.get("access_token")
    except Exception as e:
        print(f"Error saving Whoop token: {str(e)}")
        raise

def get_whoop_token(user_id):
    """Get stored Whoop token for a user"""
    try:
        response = supabase.table("whoop_tokens").select("*").eq("user_id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            return {
                "access_token": None,
                "refresh_token": None,
                "is_valid": False
            }
        
        token_data = response.data[0]
        is_valid = False
        
        # Check if token is still valid
        if token_data.get("token_expiry") and token_data.get("access_token"):
            expiry_time = datetime.fromisoformat(token_data.get("token_expiry"))
            # Check if token is still valid (with 5-minute buffer)
            is_valid = datetime.now() < (expiry_time - timedelta(minutes=5))
        
        return {
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "token_expiry": token_data.get("token_expiry"),
            "is_valid": is_valid
        }
    except Exception as e:
        print(f"Error getting Whoop token: {str(e)}")
        return {
            "access_token": None,
            "refresh_token": None,
            "is_valid": False
        }

# Metrics Storage Functions
def save_daily_metrics(user_id, metrics_data, mood_data=None):
    """Save or update daily metrics for a user"""
    try:
        date_str = metrics_data.get("date")
        if not date_str:
            date_str = datetime.today().strftime("%Y-%m-%d")
        
        # Check if metrics already exist for this date and user
        existing = supabase.table("daily_metrics").select("*").eq("user_id", user_id).eq("date", date_str).execute()
        
        # Create metrics object
        metrics_object = {
            "user_id": user_id,
            "date": date_str,
            "updated_at": datetime.now().isoformat()
        }
        
        # Add whoop metrics if provided
        if metrics_data:
            for key in [
                "recovery_score", "strain", "hrv", "resting_hr", "sleep_quality",
                "spo2_percentage", "skin_temp_celsius", "max_hr", "avg_hr", "kilojoules", 
                "sleep_consistency", "sleep_efficiency", "total_sleep_time",
                "deep_sleep_time", "rem_sleep_time", "respiratory_rate",
                "workout_count", "workout_strain"
            ]:
                if key in metrics_data and metrics_data.get(key) is not None:
                    metrics_object[key] = metrics_data.get(key)
        
        # Add mood data if provided
        if mood_data:
            if "mood_rating" in mood_data and mood_data.get("mood_rating") is not None:
                metrics_object["mood_rating"] = mood_data.get("mood_rating")
            if "notes" in mood_data and mood_data.get("notes") is not None:
                metrics_object["notes"] = mood_data.get("notes")
        
        if existing.data and len(existing.data) > 0:
            # Update existing metrics
            response = supabase.table("daily_metrics").update(metrics_object).eq("user_id", user_id).eq("date", date_str).execute()
        else:
            # Insert new metrics
            response = supabase.table("daily_metrics").insert(metrics_object).execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error saving daily metrics: {str(e)}")
        raise

def get_daily_metrics(user_id, date_str=None):
    """Get daily metrics for a user by date"""
    try:
        if date_str:
            response = supabase.table("daily_metrics").select("*").eq("user_id", user_id).eq("date", date_str).execute()
        else:
            # Get all metrics for user, sorted by date
            response = supabase.table("daily_metrics").select("*").eq("user_id", user_id).order("date", desc=True).execute()
            
        return response.data
    except Exception as e:
        print(f"Error getting daily metrics: {str(e)}")
        return []

def get_metrics_range(user_id, start_date, end_date):
    """Get metrics for a date range"""
    try:
        response = supabase.table("daily_metrics").select("*").eq("user_id", user_id).gte("date", start_date).lte("date", end_date).order("date").execute()
        return response.data
    except Exception as e:
        print(f"Error getting metrics range: {str(e)}")
        return []

# Calendar integration settings
def save_calendar_settings(user_id, settings):
    """Save user's calendar integration settings"""
    try:
        settings_object = {
            "user_id": user_id,
            "calendar_provider": settings.get("provider"),
            "calendar_id": settings.get("calendar_id"),
            "settings": json.dumps(settings),
            "updated_at": datetime.now().isoformat()
        }
        
        # Check if settings already exist for this user
        existing = supabase.table("user_settings").select("*").eq("user_id", user_id).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update existing settings
            response = supabase.table("user_settings").update(settings_object).eq("user_id", user_id).execute()
        else:
            # Insert new settings
            response = supabase.table("user_settings").insert(settings_object).execute()
            
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error saving calendar settings: {str(e)}")
        raise

def get_calendar_settings(user_id):
    """Get user's calendar integration settings"""
    try:
        response = supabase.table("user_settings").select("*").eq("user_id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            settings = response.data[0]
            if settings.get("settings"):
                try:
                    settings["settings"] = json.loads(settings["settings"])
                except:
                    settings["settings"] = {}
            return settings
        
        return None
    except Exception as e:
        print(f"Error getting calendar settings: {str(e)}")
        return None

# Initialize database tables if they don't exist
def init_supabase_tables():
    """Initialize Supabase tables if they don't exist"""
    try:
        # We use the service client for this operation
        service = get_service_client()
        
        # This SQL creates the tables if they don't exist
        # Note: This is a simplified approach; in production, you'd use migrations
        sql = """
        -- Whoop tokens table
        CREATE TABLE IF NOT EXISTS whoop_tokens (
            id SERIAL PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES auth.users(id),
            access_token TEXT,
            refresh_token TEXT,
            token_expiry TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP
        );
        
        -- Daily metrics table
        CREATE TABLE IF NOT EXISTS daily_metrics (
            id SERIAL PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES auth.users(id),
            date DATE NOT NULL,
            recovery_score FLOAT,
            hrv FLOAT,
            resting_hr FLOAT,
            spo2_percentage FLOAT,
            skin_temp_celsius FLOAT,
            strain FLOAT,
            max_hr FLOAT,
            avg_hr FLOAT,
            kilojoules FLOAT,
            sleep_quality FLOAT,
            sleep_consistency FLOAT,
            sleep_efficiency FLOAT,
            total_sleep_time FLOAT,
            deep_sleep_time FLOAT,
            rem_sleep_time FLOAT,
            respiratory_rate FLOAT,
            workout_count INTEGER,
            workout_strain FLOAT,
            mood_rating INTEGER,
            energy_level INTEGER,
            stress_level INTEGER,
            notes TEXT,
            burnout_current FLOAT,
            burnout_trend FLOAT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP,
            UNIQUE(user_id, date)
        );
        
        -- User settings table
        CREATE TABLE IF NOT EXISTS user_settings (
            id SERIAL PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES auth.users(id),
            calendar_provider TEXT,
            calendar_id TEXT,
            settings JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP,
            UNIQUE(user_id)
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_whoop_tokens_user_id ON whoop_tokens (user_id);
        CREATE INDEX IF NOT EXISTS idx_daily_metrics_user_id ON daily_metrics (user_id);
        CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_metrics (date);
        CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings (user_id);
        """
        
        # Execute the SQL to create tables
        response = service.rpc("exec_sql", {"sql": sql}).execute()
        return True
    except Exception as e:
        print(f"Error initializing Supabase tables: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the Supabase client
    print("Testing Supabase client...")
    
    # Initialize tables
    init_supabase_tables()
    
    print("Tables initialized")