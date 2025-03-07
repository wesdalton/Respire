"""
SQLite database implementation as fallback when Supabase is unavailable
"""

import os
import json
import logging
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

logger = logging.getLogger(__name__)

Base = declarative_base()
engine = None
session = None

# Models
class User(Base):
    """User model for authentication and profile data"""
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    tokens = relationship("WhoopToken", back_populates="user", cascade="all, delete-orphan")
    metrics = relationship("DailyMetrics", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSetting", back_populates="user", cascade="all, delete-orphan")

class WhoopToken(Base):
    """WHOOP API token storage"""
    __tablename__ = 'whoop_tokens'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    token_type = Column(String, default="Bearer")
    expires_in = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="tokens")

class DailyMetrics(Base):
    """Daily health metrics from WHOOP and user input"""
    __tablename__ = 'daily_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    
    # Recovery metrics
    recovery_score = Column(Float)
    hrv = Column(Float)
    resting_hr = Column(Float)
    spo2_percentage = Column(Float)
    skin_temp_celsius = Column(Float)
    
    # Strain metrics
    strain = Column(Float)
    max_hr = Column(Float)
    avg_hr = Column(Float)
    kilojoules = Column(Float)
    
    # Sleep metrics
    sleep_quality = Column(Float)
    sleep_consistency = Column(Float)
    sleep_efficiency = Column(Float)
    total_sleep_time = Column(Float)
    deep_sleep_time = Column(Float)
    rem_sleep_time = Column(Float)
    respiratory_rate = Column(Float)
    
    # Workout metrics
    workout_count = Column(Integer)
    workout_strain = Column(Float)
    
    # Subjective metrics
    mood_rating = Column(Integer)
    energy_level = Column(Integer)
    stress_level = Column(Integer)
    notes = Column(Text)
    
    # Derived metrics
    burnout_current = Column(Float)
    burnout_trend = Column(Float)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="metrics")

class UserSetting(Base):
    """User settings and preferences"""
    __tablename__ = 'user_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    settings_key = Column(String, nullable=False)
    settings_value = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="settings")

def init_sqlite(app):
    """Initialize SQLite database"""
    global engine, session
    
    # Get database URL from app config or environment
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL', 'sqlite:///burnout_predictor.db')
    
    # Create engine and session
    engine = create_engine(database_url)
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)
    
    # Create tables
    Base.metadata.create_all(engine)
    logger.info(f"SQLite database initialized at {database_url}")

# User Authentication Functions
def create_user(email, password_hash):
    """Create a new user"""
    from uuid import uuid4
    
    user = User(
        id=str(uuid4()),
        email=email,
        password_hash=password_hash
    )
    session.add(user)
    session.commit()
    return user

def get_user_by_email(email):
    """Get a user by email"""
    return session.query(User).filter_by(email=email).first()

def get_user_by_id(user_id):
    """Get a user by ID"""
    return session.query(User).filter_by(id=user_id).first()

# WHOOP Token Functions
def save_user_token(user_id, token_data):
    """Save WHOOP API token"""
    # Check if token exists
    token = session.query(WhoopToken).filter_by(user_id=user_id).first()
    
    if token:
        # Update existing token
        token.access_token = token_data.get("access_token")
        token.refresh_token = token_data.get("refresh_token")
        token.token_type = token_data.get("token_type", "Bearer")
        token.expires_in = token_data.get("expires_in", 0)
        token.updated_at = datetime.now()
    else:
        # Create new token
        token = WhoopToken(
            user_id=user_id,
            access_token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 0)
        )
        session.add(token)
    
    session.commit()
    return token

def get_user_token(user_id):
    """Get user's WHOOP token"""
    token = session.query(WhoopToken).filter_by(user_id=user_id).first()
    if not token:
        return {}
    
    return {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
        "token_type": token.token_type,
        "expires_in": token.expires_in
    }

# Metrics Functions
def add_or_update_daily_metrics(metrics_data, mood_data=None):
    """Add or update daily metrics"""
    # Get date from metrics data
    metrics_date = metrics_data.get("date")
    if isinstance(metrics_date, str):
        metrics_date = datetime.strptime(metrics_date, "%Y-%m-%d").date()
    
    # Get user ID
    user_id = metrics_data.get("user_id", "default")
    
    # Check if metrics exist for this date
    metrics = session.query(DailyMetrics).filter_by(
        user_id=user_id,
        date=metrics_date
    ).first()
    
    if metrics:
        # Update existing metrics
        for key, value in metrics_data.items():
            if hasattr(metrics, key) and key != "date" and key != "user_id":
                setattr(metrics, key, value)
        
        # Update mood data if provided
        if mood_data:
            for key, value in mood_data.items():
                if hasattr(metrics, key):
                    setattr(metrics, key, value)
    else:
        # Create new metrics
        metrics = DailyMetrics(
            user_id=user_id,
            date=metrics_date
        )
        
        # Set metrics data
        for key, value in metrics_data.items():
            if hasattr(metrics, key) and key != "date" and key != "user_id":
                setattr(metrics, key, value)
        
        # Set mood data if provided
        if mood_data:
            for key, value in mood_data.items():
                if hasattr(metrics, key):
                    setattr(metrics, key, value)
        
        session.add(metrics)
    
    session.commit()
    return metrics

def get_metrics_by_date(user_id, metrics_date):
    """Get metrics for a specific date"""
    if isinstance(metrics_date, str):
        metrics_date = datetime.strptime(metrics_date, "%Y-%m-%d").date()
    
    return session.query(DailyMetrics).filter_by(
        user_id=user_id,
        date=metrics_date
    ).first()

def get_all_metrics(user_id):
    """Get all metrics for a user"""
    return session.query(DailyMetrics).filter_by(
        user_id=user_id
    ).order_by(DailyMetrics.date.desc()).all()

def get_metrics_date_range(user_id, start_date, end_date):
    """Get metrics for a date range"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    return session.query(DailyMetrics).filter(
        DailyMetrics.user_id == user_id,
        DailyMetrics.date >= start_date,
        DailyMetrics.date < end_date
    ).order_by(DailyMetrics.date.desc()).all()

def delete_mood(user_id, metrics_date):
    """Delete mood data for a specific date"""
    metrics = get_metrics_by_date(user_id, metrics_date)
    if metrics:
        metrics.mood_rating = None
        metrics.notes = None
        session.commit()
        return True
    return False

# User Settings Functions
def save_setting(user_id, key, value):
    """Save a user setting"""
    # Check if setting exists
    setting = session.query(UserSetting).filter_by(
        user_id=user_id,
        settings_key=key
    ).first()
    
    # Convert value to JSON string if not already a string
    if not isinstance(value, str):
        value = json.dumps(value)
    
    if setting:
        # Update existing setting
        setting.settings_value = value
        setting.updated_at = datetime.now()
    else:
        # Create new setting
        setting = UserSetting(
            user_id=user_id,
            settings_key=key,
            settings_value=value
        )
        session.add(setting)
    
    session.commit()
    return setting

def get_setting(user_id, key, default=None):
    """Get a user setting"""
    setting = session.query(UserSetting).filter_by(
        user_id=user_id,
        settings_key=key
    ).first()
    
    if setting:
        try:
            # Try to parse as JSON
            return json.loads(setting.settings_value)
        except (json.JSONDecodeError, TypeError):
            # Return as string
            return setting.settings_value
    
    return default