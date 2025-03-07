"""
Add test data to the existing user account.
"""

import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Supabase client directly
from supabase import create_client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for direct table inserts
supabase = create_client(supabase_url, supabase_key)

# Get the user ID from env vars or use a fixed one
USER_ID = os.getenv("EXISTING_USER_ID", "781623e7-bd7d-4fc4-ae00-9ae5eb960682")

def generate_dummy_metrics(days=30):
    """Generate dummy metrics data for the past X days"""
    print(f"Generating dummy metrics for user: {USER_ID} for {days} days")
    
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=days)
    
    current_date = start_date
    success_count = 0
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"Creating data for {date_str}")
        
        # Generate random metrics to simulate real data
        recovery = random.randint(30, 95)  # Recovery score (0-100%)
        hrv = random.uniform(20, 120)  # Heart Rate Variability (ms)
        resting_hr = random.uniform(45, 75)  # Resting Heart Rate (bpm)
        strain = random.uniform(5.0, 18.0)  # Strain score (0-21)
        sleep_quality = random.uniform(40, 95)  # Sleep quality (%)
        mood_rating = random.randint(3, 9)  # Self-reported mood (1-10)
        
        # Create realistic correlations between metrics
        if recovery < 60:  # Poor recovery
            mood_rating = max(3, mood_rating - 2)  # Mood tends to be worse
            hrv = random.uniform(20, 60)  # HRV tends to be lower
            
        if current_date.weekday() >= 5:  # Weekend
            mood_rating = min(9, mood_rating + 1)  # Mood tends to be better
            
        # Calculate a simple burnout risk
        burnout_risk = calculate_burnout_risk(recovery, mood_rating)
        
        # Create metrics record
        metrics_data = {
            "user_id": USER_ID,
            "date": date_str,
            "recovery_score": recovery,
            "hrv": hrv,
            "resting_hr": resting_hr,
            "strain": strain,
            "sleep_quality": sleep_quality,
            "mood_rating": mood_rating, 
            "burnout_current": burnout_risk,
            "notes": generate_mood_note(mood_rating, recovery),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save directly to Supabase
        try:
            # Check if record exists
            existing = supabase.table("daily_metrics").select("*").eq("user_id", USER_ID).eq("date", date_str).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update existing record
                supabase.table("daily_metrics").update(metrics_data).eq("user_id", USER_ID).eq("date", date_str).execute()
            else:
                # Insert new record
                supabase.table("daily_metrics").insert(metrics_data).execute()
                
            success_count += 1
            print(f"  Success!")
        except Exception as e:
            print(f"  Error saving metrics for {date_str}: {str(e)}")
        
        # Move to next day
        current_date += timedelta(days=1)
    
    print(f"Successfully added {success_count} days of data")
    return success_count

def calculate_burnout_risk(recovery, mood):
    """Calculate a simple burnout risk score from metrics"""
    # Invert recovery (lower recovery = higher risk)
    recovery_factor = (100 - recovery) / 100
    
    # Invert mood (lower mood = higher risk)
    mood_factor = (10 - mood) / 10
    
    # Calculate weighted risk (0-100)
    risk = (recovery_factor * 0.7 + mood_factor * 0.3) * 100
    
    # Add some randomness
    risk = max(0, min(100, risk + random.uniform(-5, 5)))
    
    return risk

def generate_mood_note(mood, recovery):
    """Generate a realistic mood note based on mood rating and recovery"""
    if mood <= 3:
        if recovery <= 50:
            return random.choice([
                "Feeling exhausted and burned out today.",
                "Really struggling with energy levels and motivation.",
                "Need to take a mental health day soon."
            ])
        else:
            return random.choice([
                "Feeling down despite decent recovery.",
                "Emotionally drained but physically okay.",
                "Work stress is getting to me today."
            ])
    elif mood <= 6:
        if recovery <= 50:
            return random.choice([
                "Average day, but body feels tired.",
                "Doing okay mentally, but physically drained.",
                "Need more sleep tonight."
            ])
        else:
            return random.choice([
                "Feeling average today.",
                "Nothing special to report.",
                "Just a normal day."
            ])
    else:
        if recovery <= 50:
            return random.choice([
                "Surprisingly good mood despite low recovery.",
                "Mental state good, but body needs rest.",
                "Happy but tired."
            ])
        else:
            return random.choice([
                "Great day! Feeling energized and positive.",
                "Productive and focused today.",
                "Everything clicked today, feeling fantastic."
            ])

def main():
    """Main execution function"""
    print("=== Adding Test Data to Existing User Account ===")
    print(f"Using user ID: {USER_ID}")
    
    # Generate dummy metrics
    metrics_count = generate_dummy_metrics(days=30)
    
    # Summary
    print("\n=== Summary ===")
    print(f"Metrics generated: {metrics_count} days")

if __name__ == "__main__":
    main()