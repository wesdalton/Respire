// API Types
export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
  user: User;
}

export interface User {
  id: string;
  email: string;
  user_metadata?: Record<string, any>;
  created_at?: string;
}

export interface HealthMetric {
  id: string;
  user_id: string;
  date: string;
  recovery_score?: number;
  resting_hr?: number;
  hrv?: number;
  sleep_duration_minutes?: number;
  sleep_quality_score?: number;
  day_strain?: number;
  workout_count: number;
  created_at: string;
  updated_at: string;
}

export interface MoodRating {
  id: string;
  user_id: string;
  date: string;
  rating: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface BurnoutScore {
  id: string;
  user_id: string;
  date: string;
  overall_risk_score: number;
  risk_level?: string;
  risk_factors: Record<string, any>;
  confidence_score?: number;
  data_points_used?: number;
  calculated_at: string;
}

export interface AIInsight {
  id: string;
  user_id: string;
  insight_type: string;
  title: string;
  content: string;
  recommendations?: {
    items: string[];
  };
  created_at: string;
  expires_at?: string;
}

export interface DashboardData {
  user_id: string;
  metrics: {
    latest_recovery?: number;
    latest_hrv?: number;
    latest_resting_hr?: number;
    latest_strain?: number;
    latest_sleep_quality?: number;
    latest_mood?: number;
    burnout_risk_score?: number;
    burnout_trend?: string;
    days_tracked: number;
    mood_entries: number;
    last_sync?: string;
  };
  recent_health_data: HealthMetric[];
  recent_moods: MoodRating[];
  latest_burnout_score?: BurnoutScore;
  latest_insight?: AIInsight;
}

export interface WHOOPConnection {
  id: string;
  user_id: string;
  connected_at: string;
  last_synced_at?: string;
  sync_enabled: boolean;
}