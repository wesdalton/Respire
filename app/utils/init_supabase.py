"""
Initialize Supabase tables and migrate data from SQLite database.
This script should be run once when setting up Supabase integration.
"""

import os
from dotenv import load_dotenv
from app.database.supabase import (
    init_supabase_tables, sign_up, save_whoop_token, 
    save_daily_metrics, get_service_client
)
# Temporarily use old database.py for migration only
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from database import session, User, DailyMetrics, get_user_token
import uuid

# Load environment variables
load_dotenv()

def create_admin_user():
    """Create an admin user in Supabase if one doesn't exist"""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", str(uuid.uuid4()))  # Generate a random password if not set
    
    try:
        # Register admin user
        response = sign_up(admin_email, admin_password, {
            "role": "admin",
            "is_admin": True
        })
        user = response.user
        
        print(f"Admin user created with email: {admin_email}")
        print(f"User ID: {user.id}")
        
        if os.getenv("ADMIN_PASSWORD") is None:
            print(f"Generated password: {admin_password}")
            print("IMPORTANT: Save this password and set it in your .env file as ADMIN_PASSWORD")
            
        return user
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        print("The user might already exist. Try using a different email or check the Supabase dashboard.")
        return None

def migrate_whoop_tokens(admin_user_id):
    """Migrate Whoop tokens from SQLite to Supabase"""
    try:
        # Get all users from SQLite
        users = session.query(User).all()
        count = 0
        
        for user in users:
            # Get token info from SQLite
            token_info = get_user_token(user.username)
            
            if token_info.get("access_token"):
                # Create token data object
                token_data = {
                    "access_token": token_info.get("access_token"),
                    "refresh_token": token_info.get("refresh_token"),
                    "expires_in": 3600  # Default 1 hour expiry if not known
                }
                
                # Save to Supabase (for now, all under admin user)
                save_whoop_token(admin_user_id, token_data)
                count += 1
                
        print(f"Migrated {count} Whoop tokens to Supabase")
        return count
    except Exception as e:
        print(f"Error migrating Whoop tokens: {str(e)}")
        return 0

def migrate_daily_metrics(admin_user_id):
    """Migrate daily metrics from SQLite to Supabase"""
    try:
        # Get all metrics from SQLite
        metrics = session.query(DailyMetrics).all()
        count = 0
        
        for record in metrics:
            # Create metrics data object
            metrics_data = {
                "date": record.date.strftime("%Y-%m-%d"),
                "recovery_score": record.recovery_score,
                "hrv": record.hrv,
                "resting_hr": record.resting_hr,
                "strain": record.strain,
                "sleep_quality": record.sleep_quality,
                "spo2_percentage": record.spo2_percentage,
                "skin_temp_celsius": record.skin_temp_celsius,
                "max_hr": record.max_hr,
                "avg_hr": record.avg_hr,
                "kilojoules": record.kilojoules,
                "sleep_consistency": record.sleep_consistency,
                "sleep_efficiency": record.sleep_efficiency,
                "total_sleep_time": record.total_sleep_time,
                "deep_sleep_time": record.deep_sleep_time,
                "rem_sleep_time": record.rem_sleep_time,
                "respiratory_rate": record.respiratory_rate,
                "workout_count": record.workout_count,
                "workout_strain": record.workout_strain,
                "burnout_current": record.burnout_current,
                "burnout_trend": record.burnout_trend
            }
            
            # Create mood data object
            mood_data = None
            if record.mood_rating:
                mood_data = {
                    "mood_rating": record.mood_rating,
                    "notes": record.notes,
                    "energy_level": record.energy_level,
                    "stress_level": record.stress_level
                }
                
            # Save to Supabase (for now, all under admin user)
            save_daily_metrics(admin_user_id, metrics_data, mood_data)
            count += 1
            
        print(f"Migrated {count} daily metrics records to Supabase")
        return count
    except Exception as e:
        print(f"Error migrating daily metrics: {str(e)}")
        return 0

def main():
    print("Initializing Supabase for Burnout Predictor")
    print("===========================================")
    
    # Test connection to Supabase
    print("\nTesting connection to Supabase...")
    try:
        import os
        print(f"Supabase URL: {os.getenv('SUPABASE_URL')}")
        client = get_service_client()
        print("Connection successful!")
    except Exception as e:
        print(f"Error connecting to Supabase: {str(e)}")
        print("Please check your Supabase credentials in the .env file.")
        return
    
    # Try to directly create admin user first
    print("\nCreating admin user...")
    admin_user = create_admin_user()
    
    if not admin_user:
        print("Could not create admin user. Checking if tables need to be created...")
        
        # Initialize Supabase tables
        print("\nCreating database tables...")
        try:
            success = init_supabase_tables()
            
            if not success:
                print("Failed to initialize Supabase tables. Check your Supabase credentials and permissions.")
                return
                
            print("Database tables created successfully.")
            
            # Try creating admin user again
            print("\nTrying to create admin user again...")
            admin_user = create_admin_user()
            
            if not admin_user:
                print("Still could not create admin user. Check the Supabase Auth settings.")
                return
        except Exception as e:
            print(f"Error during table creation: {str(e)}")
            return
    else:
        print("Admin user created or already exists!")
    
    # Display admin user details
    print(f"\nAdmin User ID: {admin_user.id}")
    print(f"Admin Email: {admin_user.email}")
    print("\nIMPORTANT: Add this to your .env file:")
    print(f"SUPABASE_USER_ID={admin_user.id}")
        
    # Migrate data from SQLite
    print("\nMigrating data from SQLite database...")
    
    print("1. Migrating Whoop tokens...")
    migrate_whoop_tokens(admin_user.id)
    
    print("2. Migrating daily metrics...")
    migrate_daily_metrics(admin_user.id)
    
    print("\nMigration completed!")
    
    print("\nSetup completed!")
    print("You can now use the Supabase backend for authentication and data storage.")
    print(f"Make sure SUPABASE_USER_ID={admin_user.id} is in your .env file.")

if __name__ == "__main__":
    main()