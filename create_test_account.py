"""
Create a test account and populate it with dummy data.
"""

import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Supabase client
from supabase_client import (
    sign_up, save_daily_metrics, save_whoop_token
)

TEST_EMAIL = "test@yandexinc.com"
TEST_PASSWORD = "Cybersole123!"

def create_user():
    """Create test user account"""
    try:
        print(f"Creating user: {TEST_EMAIL}")
        response = sign_up(TEST_EMAIL, TEST_PASSWORD)
        user = response.user
        print(f"User created with ID: {user.id}")
        return user
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return None

def generate_dummy_token(user_id):
    """Generate and save dummy Whoop token"""
    print(f"Generating dummy Whoop token for user: {user_id}")
    
    # Create dummy token data
    token_data = {
        "access_token": f"dummy_token_{random.randint(1000, 9999)}",
        "refresh_token": f"dummy_refresh_{random.randint(1000, 9999)}",
        "expires_in": 3600 * 24 * 30  # 30 days in seconds
    }
    
    # Save token to Supabase
    try:
        save_whoop_token(user_id, token_data)
        print("Token saved successfully!")
        return True
    except Exception as e:
        print(f"Error saving token: {str(e)}")
        return False

def generate_dummy_metrics(user_id, days=30):
    """Generate dummy metrics data for the past X days"""
    print(f"Generating dummy metrics for user: {user_id} for {days} days")
    
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
            
        # Create test metrics
        metrics_data = {
            "date": date_str,
            "recovery_score": recovery,
            "hrv": hrv,
            "resting_hr": resting_hr,
            "strain": strain,
            "sleep_quality": sleep_quality,
            "burnout_current": calculate_burnout_risk(recovery, mood_rating)
        }
        
        # Create mood data
        mood_data = {
            "mood_rating": mood_rating,
            "notes": generate_mood_note(mood_rating, recovery)
        }
        
        # Save to Supabase
        try:
            save_daily_metrics(user_id, metrics_data, mood_data)
            success_count += 1
        except Exception as e:
            print(f"Error saving metrics for {date_str}: {str(e)}")
        
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
    print("=== Creating Test Account with Dummy Data ===")
    
    # Create user account
    user = create_user()
    if not user:
        print("Failed to create user. Exiting.")
        return
    
    # Add dummy Whoop token
    token_success = generate_dummy_token(user.id)
    if not token_success:
        print("Warning: Failed to add dummy token.")
    
    # Generate dummy metrics
    metrics_count = generate_dummy_metrics(user.id, days=30)
    
    # Summary
    print("\n=== Summary ===")
    print(f"User created: {TEST_EMAIL}")
    print(f"User ID: {user.id}")
    print(f"Whoop token created: {'Yes' if token_success else 'No'}")
    print(f"Metrics generated: {metrics_count} days")
    print("\nYou can now log in with these credentials:")
    print(f"Email: {TEST_EMAIL}")
    print(f"Password: {TEST_PASSWORD}")

if __name__ == "__main__":
    main()