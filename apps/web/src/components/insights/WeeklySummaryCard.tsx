import { TrendingUp, TrendingDown, Minus, AlertCircle, CheckCircle2, AlertTriangle } from 'lucide-react';
import type { WeeklySummaryData } from '../../types';

interface WeeklySummaryCardProps {
  data: WeeklySummaryData;
}

const TREND_ICONS = {
  improving: TrendingUp,
  stable: Minus,
  declining: TrendingDown,
};

const TREND_COLORS = {
  improving: 'text-green-600',
  stable: 'text-gray-600',
  declining: 'text-red-600',
};

const STATUS_COLORS = {
  good: 'bg-green-50 border-green-200 text-green-800',
  fair: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  needs_attention: 'bg-red-50 border-red-200 text-red-800',
};

const STATUS_ICONS = {
  good: CheckCircle2,
  fair: AlertTriangle,
  needs_attention: AlertCircle,
};

const PRIORITY_BADGES = {
  high: 'bg-red-100 text-red-700 border-red-300',
  medium: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  low: 'bg-blue-100 text-blue-700 border-blue-300',
};

const IMPACT_BADGES = {
  high: 'bg-purple-100 text-purple-700',
  medium: 'bg-blue-100 text-blue-700',
  low: 'bg-gray-100 text-gray-700',
};

export default function WeeklySummaryCard({ data }: WeeklySummaryCardProps) {
  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4">
        <p className="text-sm text-gray-700 leading-relaxed">{data.summary}</p>
      </div>

      {/* Key Metrics Grid */}
      {data.key_metrics && data.key_metrics.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Key Metrics</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.key_metrics.map((metric, index) => {
              const TrendIcon = TREND_ICONS[metric.trend];
              const StatusIcon = STATUS_ICONS[metric.status];

              return (
                <div
                  key={index}
                  className={`border rounded-lg p-4 ${STATUS_COLORS[metric.status]}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <StatusIcon className="w-4 h-4" />
                        <span className="font-medium text-sm">{metric.name}</span>
                      </div>
                      <div className="text-2xl font-bold">{metric.value}</div>
                    </div>
                    <div className={`flex items-center gap-1 ${TREND_COLORS[metric.trend]}`}>
                      <TrendIcon className="w-5 h-5" />
                      <span className="text-xs font-medium capitalize">{metric.trend}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Focus Areas */}
      {data.focus_areas && data.focus_areas.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Focus Areas</h4>
          <div className="space-y-2">
            {data.focus_areas.map((area, index) => (
              <div key={index} className="bg-white/60 rounded-lg p-4 border border-gray-200">
                <div className="flex items-center gap-3">
                  <div className="flex-shrink-0">
                    <span
                      className={`px-2 py-0.5 text-xs font-medium rounded border w-16 text-center ${
                        PRIORITY_BADGES[area.priority]
                      }`}
                    >
                      {area.priority}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 text-sm mb-1">{area.area}</div>
                    <p className="text-sm text-gray-600">{area.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Action Plan</h4>
          <div className="space-y-2">
            {data.recommendations.map((rec, index) => (
              <div key={index} className="bg-white/60 rounded-lg p-4 border border-gray-200">
                <div className="flex gap-3">
                  <div className="flex-shrink-0 flex items-center">
                    <div className="w-6 h-6 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center text-xs font-bold">
                      {index + 1}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-gray-500">{rec.category}</span>
                      <span className={`px-3 py-0.5 text-xs font-medium rounded w-28 text-center whitespace-nowrap ${IMPACT_BADGES[rec.impact]}`}>
                        {rec.impact} impact
                      </span>
                    </div>
                    <p className="text-sm text-gray-900">{rec.action}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
