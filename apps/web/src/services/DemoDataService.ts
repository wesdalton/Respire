import type {
  User,
  HealthMetric,
  MoodRating,
  AIInsight,
  BurnoutScore,
  DashboardData,
  WHOOPConnection,
} from '../types';
import {
  generateHealthMetrics,
  generateMoodRatings,
  generateInsights,
  generateBurnoutScores,
  generateDemoUser,
  generateWHOOPConnection,
} from './demoData';

/**
 * Demo Data Service
 * Manages demo mode data in localStorage, mimicking real API behavior
 */

const STORAGE_KEYS = {
  USER: 'demo_user',
  HEALTH_METRICS: 'demo_health_metrics',
  MOODS: 'demo_moods',
  INSIGHTS: 'demo_insights',
  BURNOUT_SCORES: 'demo_burnout_scores',
  WHOOP_CONNECTION: 'demo_whoop_connection',
  INITIALIZED: 'demo_initialized',
  INIT_TIMESTAMP: 'demo_init_timestamp',
} as const;

class DemoDataService {
  /**
   * Initialize demo data in localStorage
   */
  static initialize(): void {
    // Check if already initialized recently (within 7 days)
    const initTimestamp = localStorage.getItem(STORAGE_KEYS.INIT_TIMESTAMP);
    if (initTimestamp) {
      const daysSinceInit = (Date.now() - parseInt(initTimestamp)) / (1000 * 60 * 60 * 24);
      if (daysSinceInit < 7) {
        console.log('Demo data already initialized recently, skipping...');
        return;
      }
    }

    console.log('Initializing demo data...');

    // Generate and store all demo data
    const user = generateDemoUser();
    const healthMetrics = generateHealthMetrics();
    const moods = generateMoodRatings();
    const insights = generateInsights();
    const burnoutScores = generateBurnoutScores();
    const whoopConnection = generateWHOOPConnection();

    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
    localStorage.setItem(STORAGE_KEYS.HEALTH_METRICS, JSON.stringify(healthMetrics));
    localStorage.setItem(STORAGE_KEYS.MOODS, JSON.stringify(moods));
    localStorage.setItem(STORAGE_KEYS.INSIGHTS, JSON.stringify(insights));
    localStorage.setItem(STORAGE_KEYS.BURNOUT_SCORES, JSON.stringify(burnoutScores));
    localStorage.setItem(STORAGE_KEYS.WHOOP_CONNECTION, JSON.stringify(whoopConnection));
    localStorage.setItem(STORAGE_KEYS.INITIALIZED, 'true');
    localStorage.setItem(STORAGE_KEYS.INIT_TIMESTAMP, Date.now().toString());

    console.log('Demo data initialized successfully');
  }

  /**
   * Reset demo data to original state
   */
  static reset(): void {
    console.log('Resetting demo data...');
    Object.values(STORAGE_KEYS).forEach((key) => {
      localStorage.removeItem(key);
    });
    this.initialize();
  }

  /**
   * Clear all demo data
   */
  static clear(): void {
    console.log('Clearing demo data...');
    Object.values(STORAGE_KEYS).forEach((key) => {
      localStorage.removeItem(key);
    });
  }

  /**
   * Check if demo is initialized
   */
  static isInitialized(): boolean {
    return localStorage.getItem(STORAGE_KEYS.INITIALIZED) === 'true';
  }

  // ===== User Methods =====

  static async getCurrentUser(): Promise<User> {
    const userData = localStorage.getItem(STORAGE_KEYS.USER);
    if (!userData) {
      throw new Error('Demo user not found');
    }
    return JSON.parse(userData);
  }

  static async updateProfile(profile: {
    first_name?: string;
    last_name?: string;
    profile_picture_url?: string;
  }): Promise<User> {
    const user = await this.getCurrentUser();
    const updatedUser = {
      ...user,
      user_metadata: {
        ...user.user_metadata,
        ...profile,
      },
    };
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(updatedUser));
    return updatedUser;
  }

  // ===== Dashboard Methods =====

  static async getDashboard(): Promise<DashboardData> {
    const user = await this.getCurrentUser();
    const healthMetrics = await this.getHealthMetrics();
    const moods = await this.getMoodRatings();
    const burnoutScores = await this.getBurnoutHistory();
    const insights = await this.getInsights(1);

    // Get latest metrics
    const latestMetric = healthMetrics[healthMetrics.length - 1];
    const latestMood = moods[moods.length - 1];
    const latestBurnout = burnoutScores[burnoutScores.length - 1];

    // Calculate trend
    let burnoutTrendValue = 'stable';
    if (burnoutScores.length >= 2) {
      const current = latestBurnout.overall_risk_score;
      const previous = burnoutScores[burnoutScores.length - 2].overall_risk_score;
      if (current > previous + 5) burnoutTrendValue = 'increasing';
      else if (current < previous - 5) burnoutTrendValue = 'decreasing';
    }

    return {
      user_id: user.id,
      metrics: {
        latest_recovery: latestMetric?.recovery_score,
        latest_hrv: latestMetric?.hrv,
        latest_resting_hr: latestMetric?.resting_hr,
        latest_strain: latestMetric?.day_strain,
        latest_sleep_quality: latestMetric?.sleep_quality_score,
        latest_mood: latestMood?.rating,
        burnout_risk_score: latestBurnout?.overall_risk_score,
        burnout_trend: burnoutTrendValue,
        days_tracked: healthMetrics.length,
        mood_entries: moods.length,
        last_sync: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      },
      recent_health_data: healthMetrics.slice(-30),
      recent_moods: moods.slice(-30),
      latest_burnout_score: latestBurnout,
      latest_insight: insights[0],
    };
  }

  // ===== Health Metrics Methods =====

  static async getHealthMetrics(
    startDate?: string,
    endDate?: string,
    limit = 30
  ): Promise<HealthMetric[]> {
    const metricsData = localStorage.getItem(STORAGE_KEYS.HEALTH_METRICS);
    if (!metricsData) return [];

    let metrics: HealthMetric[] = JSON.parse(metricsData);

    // Filter by date range
    if (startDate) {
      metrics = metrics.filter((m) => m.date >= startDate);
    }
    if (endDate) {
      metrics = metrics.filter((m) => m.date <= endDate);
    }

    // Apply limit (most recent)
    if (limit) {
      metrics = metrics.slice(-limit);
    }

    return metrics;
  }

  // ===== Mood Rating Methods =====

  static async getMoodRatings(
    startDate?: string,
    endDate?: string,
    limit = 30
  ): Promise<MoodRating[]> {
    const moodsData = localStorage.getItem(STORAGE_KEYS.MOODS);
    if (!moodsData) return [];

    let moods: MoodRating[] = JSON.parse(moodsData);

    // Filter by date range
    if (startDate) {
      moods = moods.filter((m) => m.date >= startDate);
    }
    if (endDate) {
      moods = moods.filter((m) => m.date <= endDate);
    }

    // Apply limit (most recent)
    if (limit) {
      moods = moods.slice(-limit);
    }

    return moods;
  }

  static async createMoodRating(params: {
    date: string;
    rating: number;
    notes?: string;
  }): Promise<MoodRating> {
    const moodsData = localStorage.getItem(STORAGE_KEYS.MOODS);
    const moods: MoodRating[] = moodsData ? JSON.parse(moodsData) : [];
    const user = await this.getCurrentUser();

    const newMood: MoodRating = {
      id: `demo-mood-custom-${Date.now()}`,
      user_id: user.id,
      date: params.date,
      rating: params.rating,
      notes: params.notes,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Check if mood already exists for this date
    const existingIndex = moods.findIndex((m) => m.date === params.date);
    if (existingIndex >= 0) {
      moods[existingIndex] = newMood;
    } else {
      moods.push(newMood);
      // Sort by date
      moods.sort((a, b) => a.date.localeCompare(b.date));
    }

    localStorage.setItem(STORAGE_KEYS.MOODS, JSON.stringify(moods));
    return newMood;
  }

  static async updateMoodRating(
    date: string,
    rating?: number,
    notes?: string
  ): Promise<MoodRating> {
    const moodsData = localStorage.getItem(STORAGE_KEYS.MOODS);
    const moods: MoodRating[] = moodsData ? JSON.parse(moodsData) : [];

    const moodIndex = moods.findIndex((m) => m.date === date);
    if (moodIndex === -1) {
      throw new Error('Mood not found for date: ' + date);
    }

    const updatedMood = {
      ...moods[moodIndex],
      rating: rating !== undefined ? rating : moods[moodIndex].rating,
      notes: notes !== undefined ? notes : moods[moodIndex].notes,
      updated_at: new Date().toISOString(),
    };

    moods[moodIndex] = updatedMood;
    localStorage.setItem(STORAGE_KEYS.MOODS, JSON.stringify(moods));
    return updatedMood;
  }

  static async deleteMoodRating(date: string): Promise<void> {
    const moodsData = localStorage.getItem(STORAGE_KEYS.MOODS);
    if (!moodsData) return;

    let moods: MoodRating[] = JSON.parse(moodsData);
    moods = moods.filter((m) => m.date !== date);
    localStorage.setItem(STORAGE_KEYS.MOODS, JSON.stringify(moods));
  }

  static async getMoodStats(days = 30) {
    const endDate = new Date().toISOString().split('T')[0];
    const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000)
      .toISOString()
      .split('T')[0];

    const moods = await this.getMoodRatings(startDate, endDate);

    if (moods.length === 0) {
      return {
        average_rating: 0,
        total_entries: 0,
        rating_distribution: {},
      };
    }

    const sum = moods.reduce((acc, mood) => acc + mood.rating, 0);
    const average = sum / moods.length;

    const distribution: Record<number, number> = {};
    moods.forEach((mood) => {
      distribution[mood.rating] = (distribution[mood.rating] || 0) + 1;
    });

    return {
      average_rating: Math.round(average * 10) / 10,
      total_entries: moods.length,
      rating_distribution: distribution,
    };
  }

  // ===== Burnout Methods =====

  static async calculateBurnoutRisk(days = 14): Promise<BurnoutScore> {
    // In demo mode, return the most recent burnout score or generate a new one
    const scores = await this.getBurnoutHistory();
    if (scores.length > 0) {
      return scores[scores.length - 1];
    }

    // Fallback: generate a new score
    const user = await this.getCurrentUser();
    const metrics = await this.getHealthMetrics(undefined, undefined, days);
    const latestMetric = metrics[metrics.length - 1];

    return {
      id: `demo-burnout-calculated-${Date.now()}`,
      user_id: user.id,
      date: new Date().toISOString().split('T')[0],
      overall_risk_score: 35,
      risk_level: 'low',
      risk_factors: {
        recovery: latestMetric?.recovery_score || 75,
        hrv: latestMetric?.hrv || 65,
        sleep_quality: latestMetric?.sleep_quality_score || 80,
        strain: latestMetric?.day_strain || 11,
      },
      confidence_score: 88,
      data_points_used: days,
      calculated_at: new Date().toISOString(),
    };
  }

  static async getBurnoutHistory(
    startDate?: string,
    endDate?: string,
    limit = 30
  ): Promise<BurnoutScore[]> {
    const scoresData = localStorage.getItem(STORAGE_KEYS.BURNOUT_SCORES);
    if (!scoresData) return [];

    let scores: BurnoutScore[] = JSON.parse(scoresData);

    // Filter by date range
    if (startDate) {
      scores = scores.filter((s) => s.date >= startDate);
    }
    if (endDate) {
      scores = scores.filter((s) => s.date <= endDate);
    }

    // Apply limit (most recent)
    if (limit) {
      scores = scores.slice(-limit);
    }

    return scores;
  }

  // ===== AI Insights Methods =====

  static async getInsights(limit = 10): Promise<AIInsight[]> {
    const insightsData = localStorage.getItem(STORAGE_KEYS.INSIGHTS);
    if (!insightsData) return [];

    const insights: AIInsight[] = JSON.parse(insightsData);
    return insights.slice(0, limit);
  }

  static async generateInsight(insightType = 'weekly_summary', days = 14): Promise<AIInsight> {
    const user = await this.getCurrentUser();
    const now = new Date();
    const endDate = now.toISOString().split('T')[0];
    const startDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
      .toISOString()
      .split('T')[0];

    // Create a generic insight based on type
    const newInsight: AIInsight = {
      id: `demo-insight-generated-${Date.now()}`,
      user_id: user.id,
      insight_type: insightType,
      title: 'Demo Generated Insight',
      content: 'This is a demo-generated insight. In the full version, this would be based on your actual health data.',
      date_range_start: startDate,
      date_range_end: endDate,
      created_at: now.toISOString(),
    };

    // Add to insights list
    const insightsData = localStorage.getItem(STORAGE_KEYS.INSIGHTS);
    const insights: AIInsight[] = insightsData ? JSON.parse(insightsData) : [];
    insights.unshift(newInsight);
    localStorage.setItem(STORAGE_KEYS.INSIGHTS, JSON.stringify(insights));

    return newInsight;
  }

  static async updateInsightFeedback(
    insightId: string,
    helpful: boolean,
    _feedback?: string
  ): Promise<AIInsight> {
    const insightsData = localStorage.getItem(STORAGE_KEYS.INSIGHTS);
    const insights: AIInsight[] = insightsData ? JSON.parse(insightsData) : [];

    const insightIndex = insights.findIndex((i) => i.id === insightId);
    if (insightIndex === -1) {
      throw new Error('Insight not found');
    }

    insights[insightIndex] = {
      ...insights[insightIndex],
      helpful,
    };

    localStorage.setItem(STORAGE_KEYS.INSIGHTS, JSON.stringify(insights));
    return insights[insightIndex];
  }

  static async deleteInsight(insightId: string): Promise<{ message: string }> {
    const insightsData = localStorage.getItem(STORAGE_KEYS.INSIGHTS);
    if (!insightsData) {
      throw new Error('Insight not found');
    }

    let insights: AIInsight[] = JSON.parse(insightsData);
    const originalLength = insights.length;
    insights = insights.filter((i) => i.id !== insightId);

    if (insights.length === originalLength) {
      throw new Error('Insight not found');
    }

    localStorage.setItem(STORAGE_KEYS.INSIGHTS, JSON.stringify(insights));
    return { message: 'Insight deleted successfully' };
  }

  // ===== WHOOP Methods =====

  static async getWHOOPConnection(): Promise<WHOOPConnection> {
    const connectionData = localStorage.getItem(STORAGE_KEYS.WHOOP_CONNECTION);
    if (!connectionData) {
      throw new Error('WHOOP not connected');
    }
    return JSON.parse(connectionData);
  }

  static async syncWHOOP(_startDate?: string, _endDate?: string): Promise<any> {
    // Simulate sync delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // Update last_synced_at
    const connectionData = localStorage.getItem(STORAGE_KEYS.WHOOP_CONNECTION);
    if (connectionData) {
      const connection: WHOOPConnection = JSON.parse(connectionData);
      connection.last_synced_at = new Date().toISOString();
      localStorage.setItem(STORAGE_KEYS.WHOOP_CONNECTION, JSON.stringify(connection));
    }

    return {
      success: true,
      message: 'Demo sync completed',
      records_synced: 0,
      note: 'In demo mode, WHOOP sync is simulated',
    };
  }

  static async disconnectWHOOP(): Promise<void> {
    // In demo mode, just show a message - don't actually disconnect
    console.log('In demo mode, WHOOP disconnect is simulated');
  }
}

export default DemoDataService;
