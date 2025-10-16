import { useState } from 'react';
import { useHealth } from '../hooks/useHealth';
import { usePageTitle } from '../hooks/usePageTitle';
import InsightCard from '../components/dashboard/InsightCard';
import { Sparkles, RefreshCw, TrendingUp, AlertTriangle, Calendar } from 'lucide-react';
import { apiClient } from '../services/api';
import { useQueryClient } from '@tanstack/react-query';

const INSIGHT_TYPES = [
  { value: 'weekly_summary', label: 'Weekly Summary', icon: Calendar, description: 'Overview of your week' },
  { value: 'burnout_alert', label: 'Burnout Analysis', icon: AlertTriangle, description: 'Risk assessment' },
  { value: 'trend_analysis', label: 'Trend Analysis', icon: TrendingUp, description: 'Pattern insights' },
];

export default function Insights() {
  usePageTitle('AI Insights');
  const { insights, isLoading, error } = useHealth();
  const queryClient = useQueryClient();
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [selectedInsightType, setSelectedInsightType] = useState('weekly_summary');
  const [showTypeSelector, setShowTypeSelector] = useState(false);

  const handleGenerateInsight = async (insightType?: string) => {
    const typeToUse = insightType || selectedInsightType;
    setIsGenerating(true);
    setGenerateError(null);
    setShowTypeSelector(false);

    try {
      await apiClient.generateInsight(typeToUse, 14);
      // Refresh insights list
      await queryClient.invalidateQueries({ queryKey: ['insights'] });
    } catch (err) {
      setGenerateError(err instanceof Error ? err.message : 'Failed to generate insight');
    } finally {
      setIsGenerating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-12 bg-gray-200 rounded w-1/3"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
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
            <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading Insights</h2>
            <p className="text-red-600">
              {error instanceof Error ? error.message : 'Failed to load AI insights'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="bg-gradient-to-br from-purple-500 to-blue-500 p-2 rounded-lg">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-gray-900">AI Insights</h1>
            </div>
            <p className="text-gray-600">Personalized recommendations based on your health data</p>
          </div>

          <div className="relative">
            <button
              onClick={() => setShowTypeSelector(!showTypeSelector)}
              disabled={isGenerating}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw size={18} className={isGenerating ? 'animate-spin' : ''} />
              {isGenerating ? 'Generating...' : 'Generate New Insight'}
            </button>

            {/* Insight Type Dropdown */}
            {showTypeSelector && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-10 overflow-hidden">
                <div className="p-3 bg-gradient-to-r from-purple-50 to-blue-50 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-900 text-sm">Select Insight Type</h3>
                </div>
                <div className="p-2">
                  {INSIGHT_TYPES.map((type) => {
                    const Icon = type.icon;
                    return (
                      <button
                        key={type.value}
                        onClick={() => {
                          setSelectedInsightType(type.value);
                          handleGenerateInsight(type.value);
                        }}
                        className={`w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors duration-150 flex items-start gap-3 ${
                          selectedInsightType === type.value ? 'bg-purple-50 ring-1 ring-purple-200' : ''
                        }`}
                      >
                        <Icon className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <div className="font-medium text-gray-900 text-sm">{type.label}</div>
                          <div className="text-xs text-gray-500 mt-0.5">{type.description}</div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Generation Error */}
        {generateError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-800">{generateError}</p>
          </div>
        )}

        {/* Info Card */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-5">
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-1">About AI Insights</h3>
              <p className="text-sm text-blue-800">
                Our AI analyzes your health metrics, mood patterns, and burnout risk to provide personalized
                recommendations for improving your wellbeing. Insights are generated automatically and updated
                as new data becomes available.
              </p>
            </div>
          </div>
        </div>

        {/* Insights List */}
        {insights && insights.length > 0 ? (
          <div className="space-y-4">
            {insights.map((insight) => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
          </div>
        ) : (
          // Empty State
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-purple-100 to-blue-100 mb-6">
              <Sparkles className="w-10 h-10 text-purple-600" />
            </div>
            <h3 className="text-2xl font-semibold text-gray-800 mb-3">No Insights Yet</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              AI insights will be generated once you have enough health data. Keep tracking your metrics
              and mood ratings to receive personalized recommendations.
            </p>
            <button
              onClick={() => setShowTypeSelector(!showTypeSelector)}
              disabled={isGenerating}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw size={18} className={isGenerating ? 'animate-spin' : ''} />
              {isGenerating ? 'Generating...' : 'Generate Your First Insight'}
            </button>
          </div>
        )}

        {/* Insight Categories Info */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Insight Types</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-2">Sleep Optimization</h3>
              <p className="text-sm text-gray-600">
                Personalized recommendations to improve your sleep quality and recovery based on your sleep patterns.
              </p>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-2">Recovery Analysis</h3>
              <p className="text-sm text-gray-600">
                Insights on your recovery trends and suggestions for optimizing your body's ability to recover from strain.
              </p>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-2">Burnout Prevention</h3>
              <p className="text-sm text-gray-600">
                Early warning signs of burnout risk and actionable steps to maintain your mental and physical wellbeing.
              </p>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-2">Mood Patterns</h3>
              <p className="text-sm text-gray-600">
                Analysis of your mood trends and their correlation with your health metrics to identify patterns.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
