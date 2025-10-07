import { Sparkles, CheckCircle } from 'lucide-react';
import type { AIInsight } from '../../types';

interface InsightCardProps {
  insight: AIInsight;
}

const InsightCard = ({ insight }: InsightCardProps) => {
  const recommendations = insight.recommendations?.items || [];

  return (
    <div className="bg-gradient-to-br from-purple-50 via-blue-50 to-purple-50 rounded-xl shadow-sm border border-purple-100 p-6">
      <div className="flex items-start gap-3 mb-4">
        <div className="bg-gradient-to-br from-purple-500 to-blue-500 p-2 rounded-lg">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{insight.title}</h3>
          <p className="text-xs text-gray-500 mt-1">AI-Powered Insight</p>
        </div>
      </div>

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
    </div>
  );
};

export default InsightCard;
