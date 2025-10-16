import { useState } from 'react';
import { Sparkles, CheckCircle, ThumbsUp, ThumbsDown, Calendar, Clock, Trash2 } from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';
import type { AIInsight, WeeklySummaryData, BurnoutAlertData, TrendAnalysisData } from '../../types';
import { apiClient } from '../../services/api';
import { useQueryClient } from '@tanstack/react-query';
import WeeklySummaryCard from '../insights/WeeklySummaryCard';
import BurnoutAlertCard from '../insights/BurnoutAlertCard';
import TrendAnalysisCard from '../insights/TrendAnalysisCard';

interface InsightCardProps {
  insight: AIInsight;
}

const INSIGHT_TYPE_LABELS: Record<string, string> = {
  'weekly_summary': 'Weekly Summary',
  'burnout_alert': 'Burnout Analysis',
  'trend_analysis': 'Trend Analysis',
};

const InsightCard = ({ insight }: InsightCardProps) => {
  const recommendations = insight.recommendations?.items || [];
  const queryClient = useQueryClient();
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleFeedback = async (helpful: boolean) => {
    setSubmittingFeedback(true);
    try {
      await apiClient.updateInsightFeedback(insight.id, helpful);
      await queryClient.invalidateQueries({ queryKey: ['insights'] });
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this insight?')) {
      return;
    }

    setIsDeleting(true);
    try {
      await apiClient.deleteInsight(insight.id);
      await queryClient.invalidateQueries({ queryKey: ['insights'] });
    } catch (err) {
      console.error('Failed to delete insight:', err);
      alert('Failed to delete insight. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  const dateRange = insight.date_range_start && insight.date_range_end
    ? `${format(new Date(insight.date_range_start), 'MMM d')} - ${format(new Date(insight.date_range_end), 'MMM d, yyyy')}`
    : null;

  const renderStructuredInsight = () => {
    if (!insight.structured_data) return null;

    switch (insight.insight_type) {
      case 'weekly_summary':
        return <WeeklySummaryCard data={insight.structured_data as WeeklySummaryData} />;
      case 'burnout_alert':
        return <BurnoutAlertCard data={insight.structured_data as BurnoutAlertData} />;
      case 'trend_analysis':
        return <TrendAnalysisCard data={insight.structured_data as TrendAnalysisData} />;
      default:
        return null;
    }
  };

  return (
    <div className="bg-gradient-to-br from-purple-50 via-blue-50 to-purple-50 rounded-xl shadow-sm border border-purple-100 p-6">
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex items-start gap-3 flex-1">
          <div className="bg-gradient-to-br from-purple-500 to-blue-500 p-2 rounded-lg">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-lg font-semibold text-gray-900">{insight.title}</h3>
              <span className="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full font-medium">
                {INSIGHT_TYPE_LABELS[insight.insight_type] || insight.insight_type}
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-500">
              {dateRange && (
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {dateRange}
                </span>
              )}
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatDistanceToNow(new Date(insight.created_at), { addSuffix: true })}
              </span>
            </div>
          </div>
        </div>

        {/* Feedback and Action Buttons */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => handleFeedback(true)}
            disabled={submittingFeedback || insight.helpful === true || isDeleting}
            className={`p-2 rounded-lg transition-colors ${
              insight.helpful === true
                ? 'bg-green-100 text-green-600'
                : 'hover:bg-green-50 text-gray-400 hover:text-green-600'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
            title="Helpful"
          >
            <ThumbsUp className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleFeedback(false)}
            disabled={submittingFeedback || insight.helpful === false || isDeleting}
            className={`p-2 rounded-lg transition-colors ${
              insight.helpful === false
                ? 'bg-red-100 text-red-600'
                : 'hover:bg-red-50 text-gray-400 hover:text-red-600'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
            title="Not helpful"
          >
            <ThumbsDown className="w-4 h-4" />
          </button>
          <div className="w-px h-6 bg-gray-300 mx-1"></div>
          <button
            onClick={handleDelete}
            disabled={isDeleting || submittingFeedback}
            className="p-2 rounded-lg transition-colors hover:bg-red-50 text-gray-400 hover:text-red-600 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Delete insight"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Render structured content or fallback to basic content */}
      {insight.structured_data ? (
        renderStructuredInsight()
      ) : (
        <>
          <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4 mb-4">
            <p className="text-sm text-gray-700 leading-relaxed">{insight.content}</p>
          </div>

          {recommendations.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-3">Recommendations</h4>
              <div className="space-y-2">
                {recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-gray-700">{recommendation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default InsightCard;
