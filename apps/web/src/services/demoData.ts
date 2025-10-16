import type {
  User,
  HealthMetric,
  MoodRating,
  AIInsight,
  BurnoutScore,
  WHOOPConnection,
  WeeklySummaryData,
  BurnoutAlertData,
  TrendAnalysisData,
} from '../types';

/**
 * Demo Data Generator
 * Creates realistic mock data for demo mode with a compelling story arc:
 * - Days 1-25: Healthy baseline
 * - Days 26-40: Stress accumulation and burnout
 * - Days 41-60: Recovery period
 * - Days 61-90: Stabilization
 */

const DEMO_USER_ID = 'demo-user-12345';
const DEMO_START_DATE = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000); // 90 days ago

// Helper function to generate a date string
function getDateString(daysAgo: number): string {
  const date = new Date(DEMO_START_DATE);
  date.setDate(date.getDate() + daysAgo);
  return date.toISOString().split('T')[0];
}

// Helper to add random variance
function addVariance(base: number, variance: number): number {
  return base + (Math.random() * variance * 2 - variance);
}

// Helper to generate realistic patterns with trends
function generateMetricWithTrend(
  day: number,
  baseValue: number,
  variance: number,
  trendModifier: (day: number) => number
): number {
  const trend = trendModifier(day);
  const value = addVariance(baseValue * trend, variance);
  return Math.max(0, Math.round(value * 10) / 10);
}

/**
 * Generate 90 days of realistic health metrics with story arc
 */
export function generateHealthMetrics(): HealthMetric[] {
  const metrics: HealthMetric[] = [];

  for (let day = 0; day < 90; day++) {
    const date = getDateString(day);
    const now = new Date().toISOString();

    // Story arc trend modifiers
    let recoveryTrend = 1.0;
    let hrvTrend = 1.0;
    let sleepTrend = 1.0;
    let strainMultiplier = 1.0;

    // Days 1-25: Healthy baseline
    if (day < 25) {
      recoveryTrend = 1.0;
      hrvTrend = 1.0;
      sleepTrend = 1.0;
      strainMultiplier = 1.0;
    }
    // Days 26-40: Stress accumulation (declining)
    else if (day >= 25 && day < 40) {
      const stressProgress = (day - 25) / 15;
      recoveryTrend = 1.0 - stressProgress * 0.35; // Drop to 65%
      hrvTrend = 1.0 - stressProgress * 0.3;
      sleepTrend = 1.0 - stressProgress * 0.25;
      strainMultiplier = 1.0 + stressProgress * 0.3; // Increased strain
    }
    // Days 41-60: Recovery period (improving)
    else if (day >= 40 && day < 60) {
      const recoveryProgress = (day - 40) / 20;
      recoveryTrend = 0.65 + recoveryProgress * 0.25; // Recover to 90%
      hrvTrend = 0.7 + recoveryProgress * 0.25;
      sleepTrend = 0.75 + recoveryProgress * 0.2;
      strainMultiplier = 1.3 - recoveryProgress * 0.2;
    }
    // Days 61-90: Stabilization
    else {
      recoveryTrend = 0.9 + Math.random() * 0.1;
      hrvTrend = 0.95 + Math.random() * 0.05;
      sleepTrend = 0.95 + Math.random() * 0.05;
      strainMultiplier = 1.0;
    }

    // Generate metrics with trends
    const recovery = generateMetricWithTrend(day, 75, 8, () => recoveryTrend);
    const hrv = generateMetricWithTrend(day, 65, 10, () => hrvTrend);
    const restingHr = generateMetricWithTrend(
      day,
      58,
      4,
      () => 1.0 + (1.0 - hrvTrend) * 0.3 // HR increases when HRV decreases
    );
    const sleepQuality = generateMetricWithTrend(day, 80, 8, () => sleepTrend);
    const sleepDuration = generateMetricWithTrend(day, 420, 45, () => sleepTrend); // ~7 hours
    const dayStrain = generateMetricWithTrend(day, 11, 3, () => strainMultiplier);

    // Occasional workout days (3-4 per week)
    const workoutCount = Math.random() < 0.5 ? (Math.random() < 0.3 ? 2 : 1) : 0;

    metrics.push({
      id: `demo-metric-${day}`,
      user_id: DEMO_USER_ID,
      date,
      recovery_score: recovery,
      resting_hr: Math.round(restingHr),
      hrv: hrv,
      sleep_duration_minutes: Math.round(sleepDuration),
      sleep_quality_score: sleepQuality,
      day_strain: dayStrain,
      workout_count: workoutCount,
      created_at: now,
      updated_at: now,
    });
  }

  return metrics;
}

/**
 * Generate mood ratings (not every day - realistic usage)
 */
export function generateMoodRatings(): MoodRating[] {
  const moods: MoodRating[] = [];
  const metrics = generateHealthMetrics();

  for (let day = 0; day < 90; day++) {
    // 85% chance of logging mood (realistic usage)
    if (Math.random() < 0.85) {
      const date = getDateString(day);
      const now = new Date().toISOString();
      const metric = metrics[day];

      // Mood correlates with recovery score
      const recoveryInfluence = (metric.recovery_score || 70) / 100;
      const baseMood = 5 + recoveryInfluence * 4; // Range: 5-9
      const mood = Math.max(3, Math.min(10, Math.round(addVariance(baseMood, 0.8))));

      // Add notes occasionally
      let notes: string | undefined;
      if (Math.random() < 0.3) {
        const noteOptions = [
          mood >= 8 ? 'Feeling great today! High energy.' : undefined,
          mood >= 7 ? 'Good day overall, staying consistent.' : undefined,
          mood <= 5 ? 'Feeling a bit worn down.' : undefined,
          mood <= 4 ? 'Really struggling today, need more rest.' : undefined,
          mood >= 7 && metric.workout_count > 0 ? 'Great workout today!' : undefined,
          'Stressful day at work',
          'Slept poorly last night',
          'Feeling much better after rest day',
        ].filter(Boolean);
        notes = noteOptions[Math.floor(Math.random() * noteOptions.length)];
      }

      moods.push({
        id: `demo-mood-${day}`,
        user_id: DEMO_USER_ID,
        date,
        rating: mood,
        notes,
        created_at: now,
        updated_at: now,
      });
    }
  }

  return moods;
}

/**
 * Generate AI insights (weekly summaries, burnout alerts, trend analyses)
 */
export function generateInsights(): AIInsight[] {
  const insights: AIInsight[] = [];

  // Weekly Summary Insights (6 total, roughly every 15 days)
  const weeklySummaries = [
    {
      days: 0,
      title: 'Strong Start - Maintaining Balance',
      summary: 'Your metrics show excellent balance between training and recovery.',
      keyMetrics: [
        { name: 'Recovery', value: '78%', trend: 'stable' as const, status: 'good' as const },
        { name: 'HRV', value: '68ms', trend: 'stable' as const, status: 'good' as const },
        { name: 'Sleep Quality', value: '82%', trend: 'stable' as const, status: 'good' as const },
      ],
      recommendations: [
        { category: 'Recovery', action: 'Continue current training load', impact: 'medium' as const },
        { category: 'Sleep', action: 'Maintain consistent sleep schedule', impact: 'high' as const },
      ],
    },
    {
      days: 20,
      title: 'Peak Performance Period',
      summary: 'Your recovery and performance metrics are at their highest.',
      keyMetrics: [
        { name: 'Recovery', value: '84%', trend: 'improving' as const, status: 'good' as const },
        { name: 'Strain', value: '13.2', trend: 'stable' as const, status: 'good' as const },
        { name: 'Mood', value: '8/10', trend: 'improving' as const, status: 'good' as const },
      ],
      recommendations: [
        { category: 'Training', action: 'Good time for challenging workouts', impact: 'high' as const },
        { category: 'Monitoring', action: 'Watch for early signs of overtraining', impact: 'medium' as const },
      ],
    },
    {
      days: 32,
      title: 'Early Warning Signs Detected',
      summary: 'Several metrics showing decline. Time to prioritize recovery.',
      keyMetrics: [
        { name: 'Recovery', value: '58%', trend: 'declining' as const, status: 'needs_attention' as const },
        { name: 'HRV', value: '48ms', trend: 'declining' as const, status: 'needs_attention' as const },
        { name: 'Sleep', value: '6.5hrs', trend: 'declining' as const, status: 'fair' as const },
      ],
      recommendations: [
        { category: 'Recovery', action: 'Reduce training intensity by 30%', impact: 'high' as const },
        { category: 'Sleep', action: 'Prioritize 8+ hours of sleep', impact: 'high' as const },
        { category: 'Stress', action: 'Add stress management activities', impact: 'medium' as const },
      ],
    },
    {
      days: 48,
      title: 'Recovery Progress Showing',
      summary: 'Positive trends emerging after prioritizing rest and recovery.',
      keyMetrics: [
        { name: 'Recovery', value: '68%', trend: 'improving' as const, status: 'fair' as const },
        { name: 'HRV', value: '58ms', trend: 'improving' as const, status: 'fair' as const },
        { name: 'Mood', value: '7/10', trend: 'improving' as const, status: 'good' as const },
      ],
      recommendations: [
        { category: 'Training', action: 'Gradually increase activity', impact: 'medium' as const },
        { category: 'Monitoring', action: 'Continue tracking recovery closely', impact: 'high' as const },
      ],
    },
    {
      days: 65,
      title: 'Back to Baseline',
      summary: 'Metrics stabilized at healthy levels. Good balance restored.',
      keyMetrics: [
        { name: 'Recovery', value: '76%', trend: 'stable' as const, status: 'good' as const },
        { name: 'HRV', value: '66ms', trend: 'stable' as const, status: 'good' as const },
        { name: 'Consistency', value: '92%', trend: 'stable' as const, status: 'good' as const },
      ],
      recommendations: [
        { category: 'Maintenance', action: 'Continue current routine', impact: 'high' as const },
        { category: 'Prevention', action: 'Remember early warning signs', impact: 'medium' as const },
      ],
    },
    {
      days: 82,
      title: 'Sustained Progress',
      summary: 'Excellent consistency and balance over the past month.',
      keyMetrics: [
        { name: 'Recovery', value: '80%', trend: 'stable' as const, status: 'good' as const },
        { name: 'Mood', value: '8/10', trend: 'stable' as const, status: 'good' as const },
        { name: 'Sleep Quality', value: '85%', trend: 'improving' as const, status: 'good' as const },
      ],
      recommendations: [
        { category: 'Consistency', action: 'Keep up the excellent habits', impact: 'high' as const },
        { category: 'Optimization', action: 'Fine-tune training for goals', impact: 'medium' as const },
      ],
    },
  ];

  weeklySummaries.forEach((summary, index) => {
    const startDate = getDateString(summary.days);
    const endDate = getDateString(summary.days + 7);
    const createdAt = new Date(new Date(startDate).getTime() + 7 * 24 * 60 * 60 * 1000).toISOString();

    const structuredData: WeeklySummaryData = {
      title: summary.title,
      summary: summary.summary,
      key_metrics: summary.keyMetrics,
      focus_areas: [
        {
          area: 'Recovery Management',
          priority: summary.keyMetrics[0].status === 'needs_attention' ? 'high' : 'medium',
          description: 'Monitor recovery trends and adjust training accordingly',
        },
      ],
      recommendations: summary.recommendations,
    };

    insights.push({
      id: `demo-insight-weekly-${index}`,
      user_id: DEMO_USER_ID,
      insight_type: 'weekly_summary',
      title: summary.title,
      content: summary.summary,
      structured_data: structuredData,
      date_range_start: startDate,
      date_range_end: endDate,
      created_at: createdAt,
    });
  });

  // Burnout Alert Insights (3 total during stress period)
  const burnoutAlerts = [
    {
      days: 30,
      level: 'moderate' as const,
      title: 'Moderate Burnout Risk Detected',
      message: 'Your recovery metrics have declined consistently over the past week.',
      warningSigns: [
        { sign: 'Recovery score below 60% for 5+ days', severity: 'high' as const },
        { sign: 'HRV trending downward', severity: 'medium' as const },
        { sign: 'Sleep quality declining', severity: 'medium' as const },
      ],
      actions: [
        { action: 'Take 1-2 rest days', why: 'Allow body to recover', timeframe: 'This week' },
        { action: 'Reduce training intensity', why: 'Prevent further decline', timeframe: 'Next 2 weeks' },
      ],
    },
    {
      days: 36,
      level: 'high' as const,
      title: 'High Burnout Risk - Action Required',
      message: 'Multiple warning signs indicate elevated burnout risk.',
      warningSigns: [
        { sign: 'Sustained low recovery (<55%)', severity: 'high' as const },
        { sign: 'HRV significantly below baseline', severity: 'high' as const },
        { sign: 'Mood declining (avg 5/10)', severity: 'medium' as const },
        { sign: 'Poor sleep quality', severity: 'high' as const },
      ],
      actions: [
        { action: 'Prioritize rest immediately', why: 'Prevent burnout progression', timeframe: 'Today' },
        { action: 'Reduce all stressors', why: 'Support recovery', timeframe: 'This week' },
        { action: 'Focus on sleep hygiene', why: 'Improve recovery quality', timeframe: 'Ongoing' },
      ],
    },
    {
      days: 43,
      level: 'moderate' as const,
      title: 'Recovery in Progress',
      message: 'Burnout risk decreasing with recent rest and recovery focus.',
      warningSigns: [
        { sign: 'Recovery improving but still below baseline', severity: 'medium' as const },
        { sign: 'HRV showing positive trend', severity: 'low' as const },
      ],
      actions: [
        { action: 'Continue prioritizing recovery', why: 'Ensure sustained improvement', timeframe: 'Next 2 weeks' },
        { action: 'Gradually resume activity', why: 'Rebuild conditioning safely', timeframe: 'This month' },
      ],
    },
  ];

  burnoutAlerts.forEach((alert, index) => {
    const date = getDateString(alert.days);

    const structuredData: BurnoutAlertData = {
      title: alert.title,
      risk_level: alert.level,
      message: alert.message,
      warning_signs: alert.warningSigns,
      immediate_actions: alert.actions,
      support_resources: [
        'Consider speaking with a healthcare provider',
        'Explore stress management techniques',
      ],
    };

    insights.push({
      id: `demo-insight-burnout-${index}`,
      user_id: DEMO_USER_ID,
      insight_type: 'burnout_alert',
      title: alert.title,
      content: alert.message,
      structured_data: structuredData,
      date_range_start: getDateString(Math.max(0, alert.days - 7)),
      date_range_end: date,
      created_at: new Date(new Date(date).getTime()).toISOString(),
    });
  });

  // Trend Analysis Insights (3 total)
  const trendAnalyses = [
    {
      days: 25,
      title: 'Positive Training Adaptation',
      overview: 'Your body is adapting well to current training load.',
      trends: [
        {
          metric: 'Recovery Score',
          direction: 'stable' as const,
          significance: 'high' as const,
          insight: 'Consistently above 75% indicates good adaptation',
        },
        {
          metric: 'HRV',
          direction: 'stable' as const,
          significance: 'high' as const,
          insight: 'Stable HRV suggests well-managed stress',
        },
      ],
      recommendations: [{ based_on: 'Current trends', action: 'Maintain training consistency' }],
    },
    {
      days: 55,
      title: 'Recovery Trajectory Improving',
      overview: 'Positive trends emerging after recovery-focused period.',
      trends: [
        {
          metric: 'Recovery Score',
          direction: 'increasing' as const,
          significance: 'high' as const,
          insight: 'Upward trend over 2 weeks indicates effective recovery',
        },
        {
          metric: 'Sleep Quality',
          direction: 'increasing' as const,
          significance: 'medium' as const,
          insight: 'Better sleep supporting overall recovery',
        },
      ],
      recommendations: [
        { based_on: 'Improving trends', action: 'Gradually increase training volume' },
      ],
    },
    {
      days: 75,
      title: 'Stable Performance Window',
      overview: 'Metrics indicate sustained optimal performance state.',
      trends: [
        {
          metric: 'Overall Balance',
          direction: 'stable' as const,
          significance: 'high' as const,
          insight: 'Good balance between stress and recovery',
        },
      ],
      recommendations: [
        { based_on: 'Stable metrics', action: 'Good time for performance goals' },
      ],
    },
  ];

  trendAnalyses.forEach((trend, index) => {
    const endDate = getDateString(trend.days);
    const startDate = getDateString(trend.days - 14);

    const structuredData: TrendAnalysisData = {
      title: trend.title,
      overview: trend.overview,
      trends: trend.trends,
      patterns: [
        { pattern: 'Weekly cycle', observation: 'Recovery dips mid-week, peaks on weekends' },
      ],
      recommendations: trend.recommendations,
    };

    insights.push({
      id: `demo-insight-trend-${index}`,
      user_id: DEMO_USER_ID,
      insight_type: 'trend_analysis',
      title: trend.title,
      content: trend.overview,
      structured_data: structuredData,
      date_range_start: startDate,
      date_range_end: endDate,
      created_at: new Date(new Date(endDate).getTime()).toISOString(),
    });
  });

  // Sort by created_at descending
  return insights.sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
}

/**
 * Generate burnout score history
 */
export function generateBurnoutScores(): BurnoutScore[] {
  const scores: BurnoutScore[] = [];
  const metrics = generateHealthMetrics();

  // Generate scores every 4-5 days
  for (let day = 0; day < 90; day += Math.random() < 0.5 ? 4 : 5) {
    const date = getDateString(day);
    const metric = metrics[day];

    // Calculate risk score based on metrics
    let riskScore = 30; // Base score

    // Recovery impact (major factor)
    if (metric.recovery_score && metric.recovery_score < 60) {
      riskScore += (60 - metric.recovery_score) * 1.5;
    }

    // HRV impact
    if (metric.hrv && metric.hrv < 50) {
      riskScore += (50 - metric.hrv) * 0.8;
    }

    // Sleep impact
    if (metric.sleep_quality_score && metric.sleep_quality_score < 70) {
      riskScore += (70 - metric.sleep_quality_score) * 0.6;
    }

    // Strain impact
    if (metric.day_strain && metric.day_strain > 15) {
      riskScore += (metric.day_strain - 15) * 2;
    }

    riskScore = Math.max(0, Math.min(100, riskScore));

    let riskLevel: string;
    if (riskScore < 30) riskLevel = 'low';
    else if (riskScore < 50) riskLevel = 'moderate';
    else if (riskScore < 70) riskLevel = 'high';
    else riskLevel = 'critical';

    scores.push({
      id: `demo-burnout-${day}`,
      user_id: DEMO_USER_ID,
      date,
      overall_risk_score: Math.round(riskScore),
      risk_level: riskLevel,
      risk_factors: {
        recovery: metric.recovery_score || 0,
        hrv: metric.hrv || 0,
        sleep_quality: metric.sleep_quality_score || 0,
        strain: metric.day_strain || 0,
      },
      confidence_score: 85 + Math.random() * 10,
      data_points_used: 14 + Math.floor(Math.random() * 7),
      calculated_at: new Date(new Date(date).getTime() + 12 * 60 * 60 * 1000).toISOString(),
    });
  }

  return scores;
}

/**
 * Generate demo user profile
 */
export function generateDemoUser(): User {
  return {
    id: DEMO_USER_ID,
    email: 'demo@respire.cloud',
    user_metadata: {
      first_name: 'Demo',
      last_name: 'User',
      profile_picture_url: undefined,
    },
    created_at: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000).toISOString(), // Account created 120 days ago
  };
}

/**
 * Generate mock WHOOP connection
 */
export function generateWHOOPConnection(): WHOOPConnection {
  return {
    id: 'demo-whoop-connection',
    user_id: DEMO_USER_ID,
    connected_at: new Date(Date.now() - 100 * 24 * 60 * 60 * 1000).toISOString(),
    last_synced_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
    sync_enabled: true,
  };
}
