-- Respire Database Schema
-- PostgreSQL/Supabase Schema for Production Deployment
-- Version: 2.0.0

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- WHOOP CONNECTIONS
-- ============================================================================
-- Stores OAuth tokens and connection status for WHOOP integration

CREATE TABLE IF NOT EXISTS whoop_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- OAuth tokens
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expires_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- WHOOP user info
    whoop_user_id TEXT,
    scope TEXT[],

    -- Connection metadata
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_synced_at TIMESTAMP WITH TIME ZONE,
    sync_enabled BOOLEAN DEFAULT TRUE,

    -- Ensure one connection per user
    UNIQUE(user_id)
);

-- Index for quick user lookups
CREATE INDEX IF NOT EXISTS idx_whoop_connections_user ON whoop_connections(user_id);
CREATE INDEX IF NOT EXISTS idx_whoop_connections_expires ON whoop_connections(token_expires_at);

-- ============================================================================
-- HEALTH METRICS
-- ============================================================================
-- Normalized health data from WHOOP API

CREATE TABLE IF NOT EXISTS health_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,

    -- Recovery metrics
    recovery_score INTEGER CHECK (recovery_score >= 0 AND recovery_score <= 100),
    resting_hr INTEGER CHECK (resting_hr > 0),
    hrv DECIMAL(10,2) CHECK (hrv >= 0),

    -- Sleep metrics
    sleep_duration_minutes INTEGER CHECK (sleep_duration_minutes >= 0),
    sleep_quality_score INTEGER CHECK (sleep_quality_score >= 0 AND sleep_quality_score <= 100),
    sleep_latency_minutes INTEGER CHECK (sleep_latency_minutes >= 0),
    time_in_bed_minutes INTEGER CHECK (time_in_bed_minutes >= 0),
    sleep_consistency_score INTEGER,

    -- Strain metrics
    day_strain DECIMAL(5,2) CHECK (day_strain >= 0 AND day_strain <= 21),
    workout_count INTEGER DEFAULT 0,
    average_hr INTEGER,
    max_hr INTEGER,

    -- Metadata
    raw_data JSONB,  -- Store full WHOOP API response for future analysis
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure one record per user per date
    UNIQUE(user_id, date)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_health_metrics_user_date ON health_metrics(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_health_metrics_date ON health_metrics(date DESC);

-- ============================================================================
-- MOOD RATINGS
-- ============================================================================
-- User-reported mood data

CREATE TABLE IF NOT EXISTS mood_ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 10),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- One mood rating per user per date
    UNIQUE(user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_mood_ratings_user_date ON mood_ratings(user_id, date DESC);

-- ============================================================================
-- BURNOUT SCORES
-- ============================================================================
-- Calculated burnout risk scores

CREATE TABLE IF NOT EXISTS burnout_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,

    -- Risk scores (0-100)
    overall_risk_score DECIMAL(5,2) NOT NULL CHECK (overall_risk_score >= 0 AND overall_risk_score <= 100),

    -- Individual factor scores
    risk_factors JSONB NOT NULL,  -- {recovery: 75, mood: 80, hrv: 60, sleep: 70, strain_balance: 65}

    -- Confidence and metadata
    confidence_score DECIMAL(5,2) CHECK (confidence_score >= 0 AND confidence_score <= 100),
    data_points_used INTEGER,

    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- One score per user per date
    UNIQUE(user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_burnout_scores_user_date ON burnout_scores(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_burnout_scores_risk ON burnout_scores(overall_risk_score DESC);

-- ============================================================================
-- AI INSIGHTS
-- ============================================================================
-- Cached AI-generated insights and recommendations

CREATE TABLE IF NOT EXISTS ai_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Insight metadata
    insight_type TEXT NOT NULL,  -- 'daily', 'weekly', 'alert', 'recommendation'
    date_range_start DATE,
    date_range_end DATE,

    -- Content
    title TEXT,
    content TEXT NOT NULL,
    recommendations JSONB,  -- [{"action": "...", "priority": "high", "reason": "..."}]

    -- Metrics used for generation
    metrics_snapshot JSONB,

    -- AI metadata
    model_used TEXT DEFAULT 'gpt-4',
    tokens_used INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,  -- For cache invalidation

    -- User feedback
    helpful BOOLEAN,
    user_feedback TEXT
);

CREATE INDEX IF NOT EXISTS idx_ai_insights_user ON ai_insights(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_insights_type ON ai_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_ai_insights_expires ON ai_insights(expires_at);

-- ============================================================================
-- SYNC JOBS
-- ============================================================================
-- Track background data synchronization jobs

CREATE TABLE IF NOT EXISTS sync_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Job details
    job_type TEXT NOT NULL,  -- 'manual', 'scheduled', 'webhook'
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'

    -- Data synced
    data_types TEXT[],  -- ['recovery', 'sleep', 'workout']
    date_range_start DATE,
    date_range_end DATE,

    -- Results
    records_fetched INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,

    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,

    -- Error handling
    error_message TEXT,
    error_details JSONB,
    retry_count INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sync_jobs_user ON sync_jobs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sync_jobs_status ON sync_jobs(status);

-- ============================================================================
-- USER PREFERENCES
-- ============================================================================
-- User settings and preferences

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Notification preferences
    email_notifications BOOLEAN DEFAULT TRUE,
    daily_summary BOOLEAN DEFAULT TRUE,
    burnout_alerts BOOLEAN DEFAULT TRUE,

    -- Data preferences
    auto_sync_enabled BOOLEAN DEFAULT TRUE,
    sync_frequency_hours INTEGER DEFAULT 24,

    -- Privacy
    share_anonymous_data BOOLEAN DEFAULT FALSE,

    -- Display preferences
    timezone TEXT DEFAULT 'UTC',
    date_format TEXT DEFAULT 'YYYY-MM-DD',
    units_system TEXT DEFAULT 'metric',  -- 'metric' or 'imperial'

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================
-- Ensure users can only access their own data

-- Enable RLS on all tables
ALTER TABLE whoop_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE mood_ratings ENABLE ROW LEVEL SECURITY;
ALTER TABLE burnout_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Policies for whoop_connections
CREATE POLICY "Users can view own WHOOP connection"
    ON whoop_connections FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own WHOOP connection"
    ON whoop_connections FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own WHOOP connection"
    ON whoop_connections FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own WHOOP connection"
    ON whoop_connections FOR DELETE
    USING (auth.uid() = user_id);

-- Policies for health_metrics
CREATE POLICY "Users can view own health metrics"
    ON health_metrics FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own health metrics"
    ON health_metrics FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own health metrics"
    ON health_metrics FOR UPDATE
    USING (auth.uid() = user_id);

-- Policies for mood_ratings
CREATE POLICY "Users can manage own mood ratings"
    ON mood_ratings FOR ALL
    USING (auth.uid() = user_id);

-- Policies for burnout_scores
CREATE POLICY "Users can view own burnout scores"
    ON burnout_scores FOR SELECT
    USING (auth.uid() = user_id);

-- Policies for ai_insights
CREATE POLICY "Users can view own AI insights"
    ON ai_insights FOR SELECT
    USING (auth.uid() = user_id);

-- Policies for sync_jobs
CREATE POLICY "Users can view own sync jobs"
    ON sync_jobs FOR SELECT
    USING (auth.uid() = user_id);

-- Policies for user_preferences
CREATE POLICY "Users can manage own preferences"
    ON user_preferences FOR ALL
    USING (auth.uid() = user_id);

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_health_metrics_updated_at
    BEFORE UPDATE ON health_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mood_ratings_updated_at
    BEFORE UPDATE ON mood_ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View for latest metrics per user
CREATE OR REPLACE VIEW latest_health_metrics AS
SELECT DISTINCT ON (user_id)
    user_id,
    date,
    recovery_score,
    resting_hr,
    hrv,
    sleep_quality_score,
    day_strain,
    created_at
FROM health_metrics
ORDER BY user_id, date DESC;

-- View for user dashboard summary
CREATE OR REPLACE VIEW user_dashboard_summary AS
SELECT
    hm.user_id,
    hm.date,
    hm.recovery_score,
    hm.hrv,
    hm.sleep_quality_score,
    hm.day_strain,
    mr.rating as mood_rating,
    bs.overall_risk_score as burnout_risk,
    wc.last_synced_at
FROM health_metrics hm
LEFT JOIN mood_ratings mr ON hm.user_id = mr.user_id AND hm.date = mr.date
LEFT JOIN burnout_scores bs ON hm.user_id = bs.user_id AND hm.date = bs.date
LEFT JOIN whoop_connections wc ON hm.user_id = wc.user_id
ORDER BY hm.user_id, hm.date DESC;

-- ============================================================================
-- SAMPLE DATA (for development/testing)
-- ============================================================================
-- Uncomment to insert sample data

/*
-- Note: This requires a valid user_id from auth.users
-- Replace 'YOUR_USER_ID_HERE' with actual UUID

INSERT INTO whoop_connections (user_id, access_token, refresh_token, token_expires_at, whoop_user_id)
VALUES (
    'YOUR_USER_ID_HERE',
    'sample_access_token',
    'sample_refresh_token',
    NOW() + INTERVAL '1 hour',
    'whoop_12345'
);
*/

-- ============================================================================
-- MAINTENANCE
-- ============================================================================

-- Function to clean up expired AI insights
CREATE OR REPLACE FUNCTION cleanup_expired_insights()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM ai_insights
    WHERE expires_at IS NOT NULL AND expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old sync jobs (keep last 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_sync_jobs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sync_jobs
    WHERE created_at < NOW() - INTERVAL '30 days'
    AND status IN ('completed', 'failed');

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMPLETED!
-- ============================================================================

-- Grant appropriate permissions (adjust as needed for your setup)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Verify tables created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;