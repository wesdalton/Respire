"""
Initialize the database with the updated schema.
This script drops all existing tables and recreates them.
"""

from database import Base, engine, session
from datetime import datetime, timedelta
import random

# Recreate all tables
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

print("Database schema recreated successfully.")

# Generate some test data if needed
def generate_test_data(days=30):
    """Generate random test data for the past N days"""
    from database import DailyMetrics, add_or_update_daily_metrics
    
    today = datetime.now().date()
    
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # Generate random WHOOP-like metrics
        recovery = random.randint(30, 95)
        strain = random.uniform(4.0, 17.0)
        hrv = random.uniform(30.0, 90.0)
        rhr = random.uniform(45.0, 70.0)
        sleep_quality = random.uniform(60.0, 95.0)
        
        # Add systematic trends for demonstration:
        # - Lower recovery on weekends (higher strain days)
        # - Pattern of declining recovery when strain is high multiple days
        weekday = date.weekday()
        if weekday >= 5:  # Weekend
            recovery = max(30, recovery - 15)  # Lower recovery
            strain = min(21, strain + 4)  # Higher strain
        
        # Every ~10 days, simulate a period of higher burnout risk
        if (days - i) % 10 < 3:
            recovery = max(30, recovery - 20)
            hrv = max(25, hrv - 15)
            sleep_quality = max(40, sleep_quality - 25)
            
        # Create test metrics with comprehensive data
        metrics = {
            "date": date_str,
            
            # Recovery metrics
            "recovery_score": recovery,
            "hrv": hrv,
            "resting_hr": rhr,
            "spo2_percentage": random.uniform(94.0, 99.0),
            "skin_temp_celsius": random.uniform(33.0, 36.0),
            
            # Strain metrics
            "strain": strain,
            "max_hr": random.uniform(120, 180),
            "avg_hr": random.uniform(60, 100),
            "kilojoules": random.uniform(1500, 3500),
            
            # Sleep metrics
            "sleep_quality": sleep_quality,
            "sleep_consistency": random.uniform(60.0, 95.0),
            "sleep_efficiency": random.uniform(70.0, 95.0),
            "total_sleep_time": random.uniform(360, 540),  # 6-9 hours in minutes
            "deep_sleep_time": random.uniform(60, 120),    # 1-2 hours in minutes
            "rem_sleep_time": random.uniform(90, 150),     # 1.5-2.5 hours in minutes
            "respiratory_rate": random.uniform(14.0, 18.0),
            
            # Workout metrics - more workouts on certain days
            "workout_count": 1 if random.random() < 0.7 else (2 if random.random() < 0.3 else 0),
            "workout_strain": random.uniform(5.0, 15.0) if random.random() < 0.7 else 0,
            
            # Subjective metrics - add energy and stress levels
            "energy_level": random.randint(3, 8),
            "stress_level": random.randint(2, 8)
        }
        
        # Add correlation between metrics
        # Lower recovery → lower energy levels
        if metrics["recovery_score"] < 50:
            metrics["energy_level"] = max(1, metrics["energy_level"] - 3)
            
        # Higher strain → higher stress levels
        if metrics["strain"] > 12:
            metrics["stress_level"] = min(10, metrics["stress_level"] + 2)
            
        # Higher stress → lower sleep quality
        if metrics["stress_level"] > 6:
            metrics["sleep_quality"] = max(40, metrics["sleep_quality"] - 20)
            
        # Add mood ratings for all days to ensure we have correlation data
        # Base mood on recovery score with some randomness
        base_mood = ((metrics["recovery_score"] / 100) * 9) + 1  # Map 0-100 to 1-10
        random_factor = random.uniform(-2, 2)  # Add some randomness
        mood = max(1, min(10, round(base_mood + random_factor)))
        
        # Lower mood if stress is high
        if metrics.get("stress_level", 0) > 7:
            mood = max(1, mood - 2)
            
        # Save the mood rating
        metrics["mood_rating"] = mood
        
        # Add or update the record
        add_or_update_daily_metrics(metrics)
        print(f"Added test data for {date_str}")
    
    print(f"Generated test data for {days} days")

# Generate test data with a full month of data
print("Generating test data...")
generate_test_data(30)