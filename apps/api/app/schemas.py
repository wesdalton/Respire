"""
API Request/Response Schemas using Pydantic
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_serializer
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID


# WHOOP Connection Schemas
class WHOOPConnectionBase(BaseModel):
    whoop_user_id: Optional[str] = None
    scope: Optional[List[str]] = None
    sync_enabled: bool = True


class WHOOPConnectionCreate(WHOOPConnectionBase):
    access_token: str
    refresh_token: str
    token_expires_at: datetime


class WHOOPConnectionResponse(WHOOPConnectionBase):
    id: UUID
    user_id: UUID
    connected_at: datetime
    last_synced_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Health Metrics Schemas
class HealthMetricBase(BaseModel):
    date: date
    recovery_score: Optional[int] = Field(None, ge=0, le=100)
    resting_hr: Optional[int] = Field(None, gt=0)
    hrv: Optional[float] = Field(None, ge=0)
    sleep_duration_minutes: Optional[int] = Field(None, ge=0)
    sleep_quality_score: Optional[int] = Field(None, ge=0, le=100)
    sleep_latency_minutes: Optional[int] = Field(None, ge=0)
    time_in_bed_minutes: Optional[int] = Field(None, ge=0)
    sleep_consistency_score: Optional[int] = None
    day_strain: Optional[float] = Field(None, ge=0, le=100)
    workout_count: int = 0
    average_hr: Optional[int] = None
    max_hr: Optional[int] = None


class HealthMetricCreate(HealthMetricBase):
    user_id: UUID
    raw_data: Optional[Dict[str, Any]] = None


class HealthMetricResponse(HealthMetricBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Mood Rating Schemas
class MoodRatingBase(BaseModel):
    date: date
    rating: int = Field(..., ge=1, le=10)
    notes: Optional[str] = None


class MoodRatingCreate(MoodRatingBase):
    pass  # user_id comes from authentication, not from request body


class MoodRatingUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None


class MoodRatingResponse(MoodRatingBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Burnout Score Schemas
class BurnoutScoreBase(BaseModel):
    date: date
    overall_risk_score: float = Field(..., ge=0, le=100)
    risk_factors: Dict[str, Any]
    confidence_score: Optional[float] = Field(None, ge=0, le=100)
    data_points_used: Optional[int] = None


class BurnoutScoreCreate(BurnoutScoreBase):
    user_id: UUID


class BurnoutScoreResponse(BurnoutScoreBase):
    id: UUID
    user_id: UUID
    calculated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# AI Insight Schemas
class AIInsightBase(BaseModel):
    insight_type: str
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    title: Optional[str] = None
    content: str
    recommendations: Optional[Dict[str, Any]] = None
    structured_data: Optional[Dict[str, Any]] = None
    metrics_snapshot: Optional[Dict[str, Any]] = None


class AIInsightCreate(AIInsightBase):
    user_id: UUID
    model_used: str = Field(default="gpt-4", alias="modelUsed")
    tokens_used: Optional[int] = None
    expires_at: Optional[datetime] = None

    model_config = {"protected_namespaces": ()}


class AIInsightUpdate(BaseModel):
    helpful: Optional[bool] = None
    user_feedback: Optional[str] = None


class AIInsightResponse(AIInsightBase):
    id: UUID
    user_id: UUID
    model_used: str = Field(alias="modelUsed")
    tokens_used: Optional[int] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    helpful: Optional[bool] = None
    user_feedback: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, protected_namespaces=())


# Sync Job Schemas
class SyncJobBase(BaseModel):
    job_type: str
    status: str = "pending"
    data_types: Optional[List[str]] = None
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None


class SyncJobCreate(SyncJobBase):
    user_id: UUID


class SyncJobUpdate(BaseModel):
    status: Optional[str] = None
    records_fetched: Optional[int] = None
    records_inserted: Optional[int] = None
    records_updated: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    retry_count: Optional[int] = None


class SyncJobResponse(SyncJobBase):
    id: UUID
    user_id: UUID
    records_fetched: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# User Preferences Schemas
class UserPreferencesBase(BaseModel):
    email_notifications: bool = True
    daily_summary: bool = True
    burnout_alerts: bool = True
    auto_sync_enabled: bool = True
    sync_frequency_hours: int = 24
    share_anonymous_data: bool = False
    timezone: str = "UTC"
    date_format: str = "YYYY-MM-DD"
    units_system: str = "metric"


class UserPreferencesCreate(UserPreferencesBase):
    user_id: UUID


class UserPreferencesUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    daily_summary: Optional[bool] = None
    burnout_alerts: Optional[bool] = None
    auto_sync_enabled: Optional[bool] = None
    sync_frequency_hours: Optional[int] = None
    share_anonymous_data: Optional[bool] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    units_system: Optional[str] = None


class UserPreferencesResponse(UserPreferencesBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# WHOOP OAuth Schemas
class WHOOPAuthRequest(BaseModel):
    """Request to initiate WHOOP OAuth flow"""
    redirect_uri: str = Field(..., description="Redirect URI registered with WHOOP")


class WHOOPAuthResponse(BaseModel):
    """Response with authorization URL"""
    authorization_url: str
    state: str


class WHOOPTokenExchange(BaseModel):
    """Exchange authorization code for tokens"""
    code: str
    redirect_uri: str


class WHOOPTokenResponse(BaseModel):
    """OAuth token response from WHOOP"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"
    scope: List[str]
    user_id: str


# WHOOP API v2 Response Schemas
class WHOOPUserProfile(BaseModel):
    """WHOOP user profile data"""
    user_id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class WHOOPCycleResponse(BaseModel):
    """WHOOP cycle data"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    start: datetime
    end: Optional[datetime] = None
    timezone_offset: str
    score_state: str
    score: Optional[Dict[str, Any]] = None


class WHOOPRecoveryResponse(BaseModel):
    """WHOOP recovery data"""
    cycle_id: str
    sleep_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    score_state: str
    score: Optional[Dict[str, Any]] = None


class WHOOPSleepResponse(BaseModel):
    """WHOOP sleep data"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    start: datetime
    end: datetime
    timezone_offset: str
    nap: bool
    score_state: str
    score: Optional[Dict[str, Any]] = None


class WHOOPWorkoutResponse(BaseModel):
    """WHOOP workout data"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    start: datetime
    end: datetime
    timezone_offset: str
    sport_id: int
    score_state: str
    score: Optional[Dict[str, Any]] = None


# Dashboard Summary Schemas
class DashboardMetrics(BaseModel):
    """Summary metrics for dashboard"""
    latest_recovery: Optional[int] = None
    latest_hrv: Optional[float] = None
    latest_resting_hr: Optional[int] = None
    latest_strain: Optional[float] = None
    latest_sleep_quality: Optional[int] = None
    latest_mood: Optional[int] = None
    burnout_risk_score: Optional[float] = None
    burnout_trend: Optional[str] = None
    days_tracked: int = 0
    mood_entries: int = 0
    last_sync: Optional[datetime] = None


class DashboardResponse(BaseModel):
    """Complete dashboard data"""
    user_id: UUID
    metrics: DashboardMetrics
    recent_health_data: List[HealthMetricResponse]
    recent_moods: List[MoodRatingResponse]
    latest_burnout_score: Optional[BurnoutScoreResponse] = None
    latest_insight: Optional[AIInsightResponse] = None
    pending_sync_jobs: int = 0


# Oura Connection Schemas
class OuraConnectionBase(BaseModel):
    oura_user_id: Optional[str] = None
    scope: Optional[List[str]] = None
    sync_enabled: bool = True


class OuraConnectionCreate(OuraConnectionBase):
    access_token: str
    refresh_token: str
    token_expires_at: datetime


class OuraConnectionResponse(OuraConnectionBase):
    id: str
    user_id: str
    connected_at: datetime
    last_synced_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Oura OAuth Schemas
class OuraAuthRequest(BaseModel):
    """Request to initiate Oura OAuth flow"""
    redirect_uri: str = Field(..., description="Redirect URI registered with Oura")


class OuraAuthResponse(BaseModel):
    """Response with authorization URL"""
    authorization_url: str
    state: str


class OuraTokenExchange(BaseModel):
    """Exchange authorization code for tokens"""
    code: str
    redirect_uri: str


class OuraSyncRequest(BaseModel):
    """Request to sync Oura data"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class OuraSyncResponse(BaseModel):
    """Response from Oura sync"""
    success: bool
    records_synced: int
    last_synced_at: Optional[datetime] = None


class OuraDisconnectResponse(BaseModel):
    """Response from Oura disconnect"""
    success: bool
    message: str