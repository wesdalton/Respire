import { useState } from 'react';
import { useMood } from '../hooks/useMood';
import MoodEntry from '../components/mood/MoodEntry';
import MoodHistory from '../components/mood/MoodHistory';
import { TrendingUp, TrendingDown, Minus, ArrowLeft } from 'lucide-react';
import type { MoodRating } from '../types';

export default function Mood() {
  const {
    moods,
    stats,
    isLoading,
    error,
    createMood,
    updateMood,
    deleteMood,
    isCreating,
    isUpdating,
  } = useMood();

  const [editingMood, setEditingMood] = useState<MoodRating | null>(null);

  const handleSubmit = (rating: number, notes: string) => {
    if (editingMood) {
      // Update existing mood
      updateMood({ date: editingMood.date, rating, notes });
      setEditingMood(null);
    } else {
      // Create new mood for today
      const today = new Date().toISOString().split('T')[0];
      createMood({ date: today, rating, notes });
    }
  };

  const handleEdit = (mood: MoodRating) => {
    setEditingMood(mood);
    // Scroll to top to show the form
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleCancelEdit = () => {
    setEditingMood(null);
  };

  const handleDelete = (moodDate: string) => {
    if (confirm('Are you sure you want to delete this mood rating?')) {
      deleteMood(moodDate);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-12 bg-gray-200 rounded w-1/3"></div>
            <div className="h-96 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading Moods</h2>
            <p className="text-red-600">
              {error instanceof Error ? error.message : 'Failed to load mood data'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const getTrendIcon = () => {
    if (!stats?.trend) return <Minus className="w-5 h-5 text-gray-500" />;

    if (stats.trend === 'improving') {
      return <TrendingUp className="w-5 h-5 text-green-500" />;
    } else if (stats.trend === 'declining') {
      return <TrendingDown className="w-5 h-5 text-red-500" />;
    }
    return <Minus className="w-5 h-5 text-gray-500" />;
  };

  const getTrendText = () => {
    if (!stats?.trend) return 'Stable';

    if (stats.trend === 'improving') return 'Improving';
    if (stats.trend === 'declining') return 'Declining';
    return 'Stable';
  };

  const getTrendColor = () => {
    if (!stats?.trend) return 'text-gray-600';

    if (stats.trend === 'improving') return 'text-green-600';
    if (stats.trend === 'declining') return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Mood Tracking</h1>
          <p className="text-gray-600">Track and manage your daily mood ratings</p>
        </div>

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Average Mood */}
            <div className="bg-white rounded-lg shadow-md p-5">
              <div className="text-sm font-medium text-gray-600 mb-1">Average Mood</div>
              <div className="text-3xl font-bold text-gray-900">
                {stats.statistics?.average ? stats.statistics.average.toFixed(1) : 'N/A'}
                <span className="text-lg text-gray-500">/10</span>
              </div>
              {stats.data_points !== undefined && (
                <div className="text-xs text-gray-500 mt-1">
                  Based on {stats.data_points} rating{stats.data_points !== 1 ? 's' : ''}
                </div>
              )}
            </div>

            {/* Trend */}
            <div className="bg-white rounded-lg shadow-md p-5">
              <div className="text-sm font-medium text-gray-600 mb-1">Trend</div>
              <div className="flex items-center gap-2">
                {getTrendIcon()}
                <span className={`text-2xl font-bold ${getTrendColor()}`}>
                  {getTrendText()}
                </span>
              </div>
              <div className="text-xs text-gray-500 mt-1">Last 7 days</div>
            </div>

            {/* Recent High */}
            <div className="bg-white rounded-lg shadow-md p-5">
              <div className="text-sm font-medium text-gray-600 mb-1">Recent High</div>
              <div className="text-3xl font-bold text-green-600">
                {stats.statistics?.highest || 'N/A'}
                {stats.statistics?.highest && (
                  <span className="text-lg text-gray-500">/10</span>
                )}
              </div>
              <div className="text-xs text-gray-500 mt-1">Last {stats.period_days || 30} days</div>
            </div>
          </div>
        )}

        {/* Mood Entry Form */}
        {isCreating || isUpdating ? (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">{isUpdating ? 'Updating mood...' : 'Saving mood...'}</span>
            </div>
          </div>
        ) : (
          <div className="relative">
            {editingMood && (
              <button
                onClick={handleCancelEdit}
                className="absolute -top-2 left-0 mb-4 flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span className="text-sm font-medium">Back to History</span>
              </button>
            )}
            <MoodEntry
              onSubmit={handleSubmit}
              initialRating={editingMood?.rating}
              initialNotes={editingMood?.notes || ''}
              isEditing={!!editingMood}
            />
          </div>
        )}

        {/* Mood History */}
        <MoodHistory
          moods={moods || []}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      </div>
    </div>
  );
}
