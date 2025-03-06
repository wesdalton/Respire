from sqlalchemy import Column, Integer, Float, String, Date, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, default="default")
    access_token = Column(String)
    refresh_token = Column(String)
    token_expiry = Column(DateTime)
    
    def __repr__(self):
        return f"<User(username='{self.username}')>"

class DailyMetrics(Base):
    __tablename__ = 'daily_metrics'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    
    # Recovery metrics
    recovery_score = Column(Float)  # 0-100% scale
    hrv = Column(Float)  # Heart rate variability in ms
    resting_hr = Column(Float)  # Resting heart rate in bpm
    spo2_percentage = Column(Float)  # Blood oxygen saturation %
    skin_temp_celsius = Column(Float)  # Skin temperature in Celsius
    
    # Strain metrics
    strain = Column(Float)  # 0-21 Borg scale
    max_hr = Column(Float)  # Max heart rate during day
    avg_hr = Column(Float)  # Average heart rate during day
    kilojoules = Column(Float)  # Energy expenditure
    
    # Sleep metrics
    sleep_quality = Column(Float)  # 0-100% scale
    sleep_consistency = Column(Float)  # 0-100% scale
    sleep_efficiency = Column(Float)  # 0-100% scale
    total_sleep_time = Column(Float)  # Total sleep in minutes
    deep_sleep_time = Column(Float)  # Deep sleep in minutes
    rem_sleep_time = Column(Float)  # REM sleep in minutes
    respiratory_rate = Column(Float)  # Breaths per minute
    
    # Workout metrics
    workout_count = Column(Integer)  # Number of workouts
    workout_strain = Column(Float)  # Cumulative workout strain
    
    # Subjective metrics
    mood_rating = Column(Integer)  # 1-10 scale
    energy_level = Column(Integer)  # 1-10 scale (optional additional metric)
    stress_level = Column(Integer)  # 1-10 scale (optional additional metric)
    notes = Column(String)
    
    # Derived metrics
    burnout_current = Column(Float)  # Current day burnout risk
    burnout_trend = Column(Float)   # 7-day trend (positive = worsening)
    
    def __repr__(self):
        return f"<DailyMetrics(date='{self.date}', recovery_score={self.recovery_score}, mood_rating={self.mood_rating})>"

# Create database engine and session
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///burnout_predictor.db")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def add_or_update_daily_metrics(metrics_data, mood_data=None):
    """
    Add or update a daily metrics record.
    
    Args:
        metrics_data: Dictionary containing Whoop metrics
        mood_data: Dictionary containing mood rating and notes (optional)
    """
    date_str = metrics_data.get("date")
    if not date_str:
        date_str = datetime.today().strftime("%Y-%m-%d")
    
    # Convert string date to Date object
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    # Check if record exists for this date
    record = session.query(DailyMetrics).filter_by(date=date_obj).first()
    
    if not record:
        record = DailyMetrics(date=date_obj)
    
    # Update whoop metrics if provided and not None
    if metrics_data:
        if "recovery_score" in metrics_data and metrics_data.get("recovery_score") is not None:
            record.recovery_score = metrics_data.get("recovery_score")
        if "strain" in metrics_data and metrics_data.get("strain") is not None:
            record.strain = metrics_data.get("strain")
        if "hrv" in metrics_data and metrics_data.get("hrv") is not None:
            record.hrv = metrics_data.get("hrv")
        if "resting_hr" in metrics_data and metrics_data.get("resting_hr") is not None:
            record.resting_hr = metrics_data.get("resting_hr")
        if "sleep_quality" in metrics_data and metrics_data.get("sleep_quality") is not None:
            record.sleep_quality = metrics_data.get("sleep_quality")
    
    # Update mood data if provided
    if mood_data:
        if "mood_rating" in mood_data and mood_data.get("mood_rating") is not None:
            record.mood_rating = mood_data.get("mood_rating")
        if "notes" in mood_data and mood_data.get("notes") is not None:
            record.notes = mood_data.get("notes")
    
    session.add(record)
    session.commit()
    return record

def get_all_metrics():
    """
    Retrieve all daily metrics from the database.
    Returns a list of DailyMetrics objects.
    """
    return session.query(DailyMetrics).order_by(DailyMetrics.date).all()

def get_or_create_user(username="default"):
    """
    Get the default user or create one if it doesn't exist.
    """
    user = session.query(User).filter_by(username=username).first()
    if not user:
        user = User(username=username)
        session.add(user)
        session.commit()
    return user

def save_user_token(token_data, username="default"):
    """
    Save the token information to the database for the given user.
    
    Args:
        token_data: Dictionary containing token information
        username: Username to associate with the token (default: "default")
    
    Returns:
        The access token
    """
    user = get_or_create_user(username)
    
    # Extract token information
    access_token = token_data.get("access_token", "")
    refresh_token = token_data.get("refresh_token", "")
    expires_in = token_data.get("expires_in", 0)
    
    # Calculate expiry datetime
    if expires_in:
        token_expiry = datetime.now() + timedelta(seconds=expires_in)
    else:
        token_expiry = None
    
    # Update user record
    user.access_token = access_token
    user.refresh_token = refresh_token
    user.token_expiry = token_expiry
    
    session.commit()
    return access_token

def get_user_token(username="default"):
    """
    Get the access token for the given user.
    
    Returns:
        Dictionary with access_token, refresh_token, and is_valid status
    """
    user = get_or_create_user(username)
    
    is_valid = False
    if user.token_expiry and user.access_token:
        # Check if token is still valid (with 5-minute buffer)
        is_valid = datetime.now() < (user.token_expiry - timedelta(minutes=5))
    
    return {
        "access_token": user.access_token,
        "refresh_token": user.refresh_token,
        "is_valid": is_valid
    }

if __name__ == "__main__":
    # Test the database functions
    from datetime import date, timedelta
    
    # Sample data
    test_metrics = {
        "date": "2024-12-01",
        "recovery_score": 85.5,
        "strain": 10.2,
        "hrv": 65.0,
        "resting_hr": 55.0,
        "sleep_quality": 90.0
    }
    
    test_mood = {
        "mood_rating": 8,
        "notes": "Feeling good today!"
    }
    
    # Add sample data
    add_or_update_daily_metrics(test_metrics, test_mood)
    
    # Verify data was added
    all_records = get_all_metrics()
    for record in all_records:
        print(record)
        
    # Test user token functions
    test_token = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_in": 3600
    }
    
    save_user_token(test_token)
    token_info = get_user_token()
    print(f"User token: {token_info}")