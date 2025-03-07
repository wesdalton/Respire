"""
Check existing tables in Supabase.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin operations
supabase = create_client(supabase_url, supabase_key)

def main():
    print("Checking Supabase tables...")
    
    # Test if we can access the tables
    try:
        # Try accessing whoop_tokens table
        print("\nTrying to access whoop_tokens table...")
        response = supabase.table("whoop_tokens").select("*").limit(1).execute()
        print(f"Success! Found {len(response.data)} records")
    except Exception as e:
        print(f"Error accessing whoop_tokens: {str(e)}")
        
    try:
        # Try accessing daily_metrics table
        print("\nTrying to access daily_metrics table...")
        response = supabase.table("daily_metrics").select("*").limit(1).execute()
        print(f"Success! Found {len(response.data)} records")
    except Exception as e:
        print(f"Error accessing daily_metrics: {str(e)}")
        
    try:
        # Try accessing user_settings table
        print("\nTrying to access user_settings table...")
        response = supabase.table("user_settings").select("*").limit(1).execute()
        print(f"Success! Found {len(response.data)} records")
    except Exception as e:
        print(f"Error accessing user_settings: {str(e)}")
        
    # Try creating a record
    try:
        print("\nTrying to create tables by inserting data...")
        
        # Create whoop_tokens table with a record
        print("\nCreating whoop_tokens table...")
        supabase.table("whoop_tokens").insert({
            "user_id": "174384bf-ed61-4f8b-ac38-93f2b3f340ab",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "token_expiry": "2024-01-01T00:00:00"
        }).execute()
        print("Successfully created whoop_tokens table!")
        
        # Create daily_metrics table with a record
        print("\nCreating daily_metrics table...")
        supabase.table("daily_metrics").insert({
            "user_id": "174384bf-ed61-4f8b-ac38-93f2b3f340ab",
            "date": "2024-01-01",
            "recovery_score": 80,
            "mood_rating": 7
        }).execute()
        print("Successfully created daily_metrics table!")
        
        # Create user_settings table with a record
        print("\nCreating user_settings table...")
        supabase.table("user_settings").insert({
            "user_id": "174384bf-ed61-4f8b-ac38-93f2b3f340ab",
            "calendar_provider": "google",
            "calendar_id": "primary",
            "settings": "{\"notifications\": true}"
        }).execute()
        print("Successfully created user_settings table!")
        
    except Exception as e:
        print(f"Error creating tables: {str(e)}")

if __name__ == "__main__":
    main()