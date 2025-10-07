import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

interface BurnoutGaugeProps {
  risk_score: number;
  risk_level: 'low' | 'moderate' | 'high' | 'critical';
}

const riskLevelConfig = {
  low: {
    color: '#10b981',
    label: 'Low Risk',
    description: 'You are doing great! Keep up the healthy habits.',
  },
  moderate: {
    color: '#f59e0b',
    label: 'Moderate Risk',
    description: 'Monitor your health metrics and consider stress management.',
  },
  high: {
    color: '#f97316',
    label: 'High Risk',
    description: 'Take action to reduce stress and improve recovery.',
  },
  critical: {
    color: '#ef4444',
    label: 'Critical Risk',
    description: 'Immediate attention needed. Consider professional support.',
  },
};

const BurnoutGauge = ({ risk_score, risk_level }: BurnoutGaugeProps) => {
  const config = riskLevelConfig[risk_level];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Burnout Risk</h3>

      <div className="flex flex-col items-center">
        <div className="w-48 h-48 mb-6">
          <CircularProgressbar
            value={risk_score}
            text={`${risk_score}%`}
            styles={buildStyles({
              textSize: '20px',
              pathColor: config.color,
              textColor: config.color,
              trailColor: '#f3f4f6',
              strokeLinecap: 'round',
            })}
          />
        </div>

        <div className="text-center">
          <div
            className="inline-block px-4 py-2 rounded-full text-sm font-semibold mb-3"
            style={{
              backgroundColor: `${config.color}20`,
              color: config.color,
            }}
          >
            {config.label}
          </div>
          <p className="text-sm text-gray-600 max-w-xs">{config.description}</p>
        </div>
      </div>
    </div>
  );
};

export default BurnoutGauge;
