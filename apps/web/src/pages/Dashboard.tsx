import { useState } from 'react';
import { Activity, Heart, Zap, Moon, RefreshCw, AlertCircle } from 'lucide-react';
import { useDashboard } from '../hooks/useDashboard';
import MetricsCard from '../components/dashboard/MetricsCard';
import BurnoutGauge from '../components/dashboard/BurnoutGauge';
import HealthChart from '../components/dashboard/HealthChart';
import InsightCard from '../components/dashboard/InsightCard';
import MoodEntry from '../components/mood/MoodEntry';
import { apiClient } from '../services/api';
import { useQueryClient } from '@tanstack/react-query';

export default function Dashboard() {
  const { dashboard, isLoading, error, refetch, sync, isSyncing } = useDashboard();
  const queryClient = useQueryClient();
  const [showMoodEntry, setShowMoodEntry] = useState(false);
  const [moodSubmitting, setMoodSubmitting] = useState(false);

  const handleMoodSubmit = async (rating: number, notes: string) => {
    setMoodSubmitting(true);
    const today = new Date().toISOString().split('T')[0];

    try {
      // Check if today's mood already exists
      const todaysMood = dashboard?.recent_moods?.find(m => m.date === today);

      if (todaysMood) {
        // Update existing mood
        await apiClient.updateMoodRating(today, rating, notes);
      } else {
        // Create new mood
        await apiClient.createMoodRating({
          rating,
          notes,
          date: today,
        });
      }

      // Invalidate and refetch dashboard data
      await queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setShowMoodEntry(false);
    } catch (err) {
      console.error('Failed to submit mood:', err);
    } finally {
      setMoodSubmitting(false);
    }
  };

  const handleSyncWHOOP = () => {
    sync();
  };

  const handleRetry = () => {
    refetch();
  };

  // Determine trend based on comparison with average
  const getTrend = (current?: number, threshold?: number): 'up' | 'down' | 'stable' => {
    if (!current || !threshold) return 'stable';
    if (current > threshold) return 'up';
    if (current < threshold) return 'down';
    return 'stable';
  };

  // Determine risk level from score
  const getRiskLevel = (score?: number): 'low' | 'moderate' | 'high' | 'critical' => {
    if (!score) return 'low';
    if (score < 25) return 'low';
    if (score < 50) return 'moderate';
    if (score < 75) return 'high';
    return 'critical';
  };

  // Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600 font-medium">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // Error State
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
          <div className="bg-red-50 rounded-full p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <AlertCircle className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Something went wrong</h2>
          <p className="text-gray-600 mb-6">
            {error instanceof Error ? error.message : 'Failed to load dashboard data'}
          </p>
          <button
            onClick={handleRetry}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200 inline-flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Get last 7 days of health data
  const recentHealthData = dashboard?.recent_health_data?.slice(-7) || [];
  const metrics = dashboard?.metrics;

  // Check if today's mood exists
  const today = new Date().toISOString().split('T')[0];
  const todaysMood = dashboard?.recent_moods?.find(m => m.date === today);
  const hasTodaysMood = !!todaysMood;

  // Get latest mood and check if it's from today
  const latestMood = dashboard?.recent_moods?.[0];
  const latestMoodIsToday = latestMood?.date === today;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
            <p className="text-gray-600">
              Track your health metrics and burnout risk
              {metrics?.last_sync && (
                <span className="ml-2 text-sm">
                  • Last synced: {new Date(metrics.last_sync).toLocaleString()}
                </span>
              )}
            </p>
          </div>
          <div className="flex gap-3 mt-4 sm:mt-0">
            <button
              onClick={() => setShowMoodEntry(!showMoodEntry)}
              className={`font-medium py-2 px-4 rounded-lg transition-colors duration-200 ${
                hasTodaysMood
                  ? 'bg-white hover:bg-gray-50 text-gray-700 border border-gray-200'
                  : 'bg-purple-600 hover:bg-purple-700 text-white shadow-sm'
              }`}
            >
              {showMoodEntry ? 'Hide' : hasTodaysMood ? 'Edit Mood' : 'Log Mood'}
            </button>
            <button
              onClick={handleSyncWHOOP}
              disabled={isSyncing}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
              {isSyncing ? 'Syncing...' : 'Sync WHOOP'}
            </button>
          </div>
        </div>

        {/* Mood Entry Form */}
        {showMoodEntry && (
          <div className="mb-8 animate-in fade-in slide-in-from-top-4 duration-300">
            {moodSubmitting ? (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-3"></div>
                <p className="text-gray-600">Saving your mood...</p>
              </div>
            ) : (
              <MoodEntry onSubmit={handleMoodSubmit} />
            )}
          </div>
        )}

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricsCard
            title="Recovery"
            value={metrics?.latest_recovery ?? '--'}
            unit="%"
            icon={<Activity className="w-6 h-6" />}
            trend={getTrend(metrics?.latest_recovery, 70)}
            color="blue"
          />
          <MetricsCard
            title="HRV"
            value={metrics?.latest_hrv ?? '--'}
            unit="ms"
            icon={<Heart className="w-6 h-6" />}
            trend={getTrend(metrics?.latest_hrv, 50)}
            color="green"
          />
          <MetricsCard
            title={latestMoodIsToday ? "Mood (Today)" : latestMood ? `Mood (${new Date(latestMood.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })})` : "Mood"}
            value={metrics?.latest_mood ?? '--'}
            unit="/10"
            icon={<Zap className="w-6 h-6" />}
            trend={getTrend(metrics?.latest_mood, 7)}
            color="purple"
            subtitle={!latestMoodIsToday && metrics?.latest_mood ? 'No mood logged today' : undefined}
          />
          <MetricsCard
            title="Sleep Quality"
            value={metrics?.latest_sleep_quality ?? '--'}
            unit="%"
            icon={<Moon className="w-6 h-6" />}
            trend={getTrend(metrics?.latest_sleep_quality, 75)}
            color="orange"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Burnout Gauge */}
          <div className="lg:col-span-1">
            <BurnoutGauge
              risk_score={metrics?.burnout_risk_score ?? 0}
              risk_level={getRiskLevel(metrics?.burnout_risk_score)}
            />
          </div>

          {/* Health Chart */}
          <div className="lg:col-span-2">
            {recentHealthData.length > 0 ? (
              <HealthChart
                data={recentHealthData}
                metrics={['recovery_score', 'hrv', 'sleep_quality_score', 'day_strain']}
              />
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center h-full flex flex-col items-center justify-center">
                <Activity className="w-12 h-12 text-gray-300 mb-3" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Health Data Yet</h3>
                <p className="text-gray-600 mb-4">Sync your WHOOP data to see health trends</p>
                <button
                  onClick={handleSyncWHOOP}
                  disabled={isSyncing}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 inline-flex items-center gap-2 disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
                  {isSyncing ? 'Syncing...' : 'Sync Now'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* AI Insights Section */}
        {dashboard?.latest_insight ? (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Latest Insights</h2>
            <InsightCard insight={dashboard.latest_insight} />
          </div>
        ) : (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Latest Insights</h2>
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
              <div className="bg-gray-50 rounded-full p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Zap className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No AI Insights Yet</h3>
              <p className="text-gray-600">
                Keep tracking your health metrics to receive personalized insights
              </p>
            </div>
          </div>
        )}

        {/* Stats Summary */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Progress</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">{metrics?.days_tracked ?? 0}</p>
              <p className="text-sm text-gray-600 mt-1">Days Tracked</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">
                {dashboard?.recent_moods?.length ?? 0}
              </p>
              <p className="text-sm text-gray-600 mt-1">Mood Entries</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-600">
                {recentHealthData.length}
              </p>
              <p className="text-sm text-gray-600 mt-1">Recent Data Points</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-orange-600">
                {metrics?.burnout_trend ?? 'Stable'}
              </p>
              <p className="text-sm text-gray-600 mt-1">Trend</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
