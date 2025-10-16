import { AlertTriangle, Clock, Info } from 'lucide-react';
import type { BurnoutAlertData } from '../../types';

interface BurnoutAlertCardProps {
  data: BurnoutAlertData;
}

const SEVERITY_COLORS = {
  high: 'bg-red-100 border-red-300 text-red-800',
  medium: 'bg-orange-100 border-orange-300 text-orange-800',
  low: 'bg-yellow-100 border-yellow-300 text-yellow-800',
};

const RISK_LEVEL_COLORS = {
  critical: 'bg-red-600',
  high: 'bg-orange-500',
  moderate: 'bg-yellow-500',
  low: 'bg-green-500',
};

const RISK_LEVEL_TEXT = {
  critical: 'Critical Risk',
  high: 'High Risk',
  moderate: 'Moderate Risk',
  low: 'Low Risk',
};

export default function BurnoutAlertCard({ data }: BurnoutAlertCardProps) {
  return (
    <div className="space-y-6">
      {/* Risk Level Banner */}
      <div className={`${RISK_LEVEL_COLORS[data.risk_level]} text-white rounded-lg p-4`}>
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6" />
          <div>
            <div className="font-bold text-lg">{RISK_LEVEL_TEXT[data.risk_level]}</div>
            <div className="text-sm opacity-90 mt-0.5">Immediate attention recommended</div>
          </div>
        </div>
      </div>

      {/* Message */}
      <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4 border border-gray-200">
        <p className="text-sm text-gray-700 leading-relaxed">{data.message}</p>
      </div>

      {/* Warning Signs */}
      {data.warning_signs && data.warning_signs.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Warning Signs Detected
          </h4>
          <div className="space-y-2">
            {data.warning_signs.map((sign, index) => (
              <div key={index} className={`rounded-lg p-3 border ${SEVERITY_COLORS[sign.severity]}`}>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0">
                    <span className="text-xs font-bold uppercase tracking-wide w-16 inline-block text-center">{sign.severity}</span>
                  </div>
                  <p className="text-sm flex-1">{sign.sign}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Immediate Actions */}
      {data.immediate_actions && data.immediate_actions.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Take Action Now</h4>
          <div className="space-y-3">
            {data.immediate_actions.map((action, index) => (
              <div key={index} className="bg-white rounded-lg p-4 border-l-4 border-purple-500 shadow-sm">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-0.5">
                    <div className="w-6 h-6 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center text-xs font-bold">
                      {index + 1}
                    </div>
                  </div>
                  <div className="flex-1 space-y-2">
                    <p className="text-sm font-medium text-gray-900">{action.action}</p>
                    <div className="bg-blue-50 border border-blue-200 rounded p-2">
                      <div className="flex items-start gap-2">
                        <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                        <p className="text-xs text-blue-800">{action.why}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <Clock className="w-3 h-3" />
                      <span>{action.timeframe}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Support Resources */}
      {data.support_resources && data.support_resources.length > 0 && (
        <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Support Resources</h4>
          <ul className="space-y-2">
            {data.support_resources.map((resource, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                <span className="text-purple-500 flex-shrink-0">•</span>
                <span>{resource}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
