import { TrendingUp, TrendingDown, Minus, Activity, Lightbulb } from 'lucide-react';
import type { TrendAnalysisData } from '../../types';

interface TrendAnalysisCardProps {
  data: TrendAnalysisData;
}

const DIRECTION_ICONS = {
  increasing: TrendingUp,
  stable: Minus,
  decreasing: TrendingDown,
};

const DIRECTION_COLORS = {
  increasing: 'text-green-600 bg-green-50',
  stable: 'text-gray-600 bg-gray-50',
  decreasing: 'text-red-600 bg-red-50',
};

const SIGNIFICANCE_BADGES = {
  high: 'bg-purple-100 text-purple-700 border-purple-300',
  medium: 'bg-blue-100 text-blue-700 border-blue-300',
  low: 'bg-gray-100 text-gray-700 border-gray-300',
};

export default function TrendAnalysisCard({ data }: TrendAnalysisCardProps) {
  return (
    <div className="space-y-6">
      {/* Overview */}
      <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4">
        <p className="text-sm text-gray-700 leading-relaxed">{data.overview}</p>
      </div>

      {/* Trends */}
      {data.trends && data.trends.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Metric Trends
          </h4>
          <div className="space-y-3">
            {data.trends.map((trend, index) => {
              const DirectionIcon = DIRECTION_ICONS[trend.direction];

              return (
                <div key={index} className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg ${DIRECTION_COLORS[trend.direction]}`}>
                      <DirectionIcon className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium text-gray-900">{trend.metric}</span>
                        <span
                          className={`px-2 py-0.5 text-xs font-medium rounded border whitespace-nowrap ${
                            SIGNIFICANCE_BADGES[trend.significance]
                          }`}
                        >
                          {trend.significance} significance
                        </span>
                        <span className="text-xs text-gray-500 capitalize">({trend.direction})</span>
                      </div>
                      <p className="text-sm text-gray-600">{trend.insight}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Patterns */}
      {data.patterns && data.patterns.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Lightbulb className="w-4 h-4" />
            Patterns Identified
          </h4>
          <div className="space-y-2">
            {data.patterns.map((pattern, index) => (
              <div key={index} className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200">
                <div className="font-medium text-sm text-purple-900 mb-1">{pattern.pattern}</div>
                <p className="text-sm text-gray-700">{pattern.observation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Recommendations</h4>
          <div className="space-y-3">
            {data.recommendations.map((rec, index) => (
              <div key={index} className="bg-white rounded-lg p-4 border-l-4 border-blue-500">
                <div className="flex items-center gap-3">
                  <div className="flex-shrink-0">
                    <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold">
                      {index + 1}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="text-xs font-medium text-blue-600 mb-1">Based on: {rec.based_on}</div>
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
