"""
Database Models using SQLAlchemy
"""
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Boolean, Text, ARRAY, JSON, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class WHOOPConnection(Base):
    """WHOOP OAuth connection and tokens"""
    __tablename__ = "whoop_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)

    # OAuth tokens
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)  # WHOOP may not always provide refresh tokens
    token_expires_at = Column(DateTime(timezone=True), nullable=False)

    # WHOOP user info
    whoop_user_id = Column(String)
    scope = Column(ARRAY(String))

    # Connection metadata
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_synced_at = Column(DateTime(timezone=True))
    sync_enabled = Column(Boolean, default=True)


class OuraConnection(Base):
    """Oura OAuth connection and tokens"""
    __tablename__ = "oura_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)

    # OAuth tokens
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_expires_at = Column(DateTime(timezone=True), nullable=False)

    # Oura user info
    oura_user_id = Column(String)
    scope = Column(ARRAY(String))

    # Connection metadata
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_synced_at = Column(DateTime(timezone=True))
    sync_enabled = Column(Boolean, default=True)

    # Webhook configuration (optional)
    webhook_subscription_id = Column(String)
    webhook_enabled = Column(Boolean, default=False)


class HealthMetric(Base):
    """Health metrics from WHOOP and Oura"""
    __tablename__ = "health_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    date = Column(Date, nullable=False)

    # Recovery metrics
    recovery_score = Column(Integer)
    resting_hr = Column(Integer)
    hrv = Column(Float)

    # Sleep metrics
    sleep_duration_minutes = Column(Integer)
    sleep_quality_score = Column(Integer)
    sleep_latency_minutes = Column(Integer)
    time_in_bed_minutes = Column(Integer)
    sleep_consistency_score = Column(Integer)

    # Strain metrics
    day_strain = Column(Float)
    workout_count = Column(Integer, default=0)
    average_hr = Column(Integer)
    max_hr = Column(Integer)

    # Data source tracking
    data_source = Column(String, default='whoop')  # 'whoop' or 'oura'

    # Metadata
    raw_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('recovery_score >= 0 AND recovery_score <= 100', name='check_recovery_score'),
        CheckConstraint('resting_hr > 0', name='check_resting_hr'),
    )


class MoodRating(Base):
    """User-reported mood ratings"""
    __tablename__ = "mood_ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    date = Column(Date, nullable=False)
    rating = Column(Integer, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 10', name='check_mood_rating'),
    )


class BurnoutScore(Base):
    """Calculated burnout risk scores"""
    __tablename__ = "burnout_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    date = Column(Date, nullable=False)

    overall_risk_score = Column(Float, nullable=False)
    risk_factors = Column(JSONB, nullable=False)
    confidence_score = Column(Float)
    data_points_used = Column(Integer)

    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint('overall_risk_score >= 0 AND overall_risk_score <= 100', name='check_burnout_score'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 100', name='check_confidence_score'),
    )


class AIInsight(Base):
    """AI-generated insights and recommendations"""
    __tablename__ = "ai_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)

    insight_type = Column(String, nullable=False)
    date_range_start = Column(Date)
    date_range_end = Column(Date)

    title = Column(Text)
    content = Column(Text, nullable=False)
    recommendations = Column(JSONB)
    structured_data = Column(JSONB)  # New: Store structured insight data for rich UI

    metrics_snapshot = Column(JSONB)

    model_used = Column(String, default='gpt-4')
    tokens_used = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))

    helpful = Column(Boolean)
    user_feedback = Column(Text)


class SyncJob(Base):
    """Background sync job tracking"""
    __tablename__ = "sync_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)

    job_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default='pending')

    data_types = Column(ARRAY(String))
    date_range_start = Column(Date)
    date_range_end = Column(Date)

    records_fetched = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)

    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)

    error_message = Column(Text)
    error_details = Column(JSONB)
    retry_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserPreferences(Base):
    """User settings and preferences"""
    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=True), primary_key=True)

    email_notifications = Column(Boolean, default=True)
    daily_summary = Column(Boolean, default=True)
    burnout_alerts = Column(Boolean, default=True)

    auto_sync_enabled = Column(Boolean, default=True)
    sync_frequency_hours = Column(Integer, default=24)

    share_anonymous_data = Column(Boolean, default=False)

    timezone = Column(String, default='UTC')
    date_format = Column(String, default='YYYY-MM-DD')
    units_system = Column(String, default='metric')

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())