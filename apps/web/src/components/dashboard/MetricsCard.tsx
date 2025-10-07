import { ReactNode } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricsCardProps {
  title: string;
  value: number | string;
  unit: string;
  icon: ReactNode;
  trend: 'up' | 'down' | 'stable';
  color: 'blue' | 'green' | 'purple' | 'orange';
  subtitle?: string;
}

const colorClasses = {
  blue: {
    bg: 'bg-blue-50',
    icon: 'text-blue-600',
    trend: 'text-blue-600',
  },
  green: {
    bg: 'bg-green-50',
    icon: 'text-green-600',
    trend: 'text-green-600',
  },
  purple: {
    bg: 'bg-purple-50',
    icon: 'text-purple-600',
    trend: 'text-purple-600',
  },
  orange: {
    bg: 'bg-orange-50',
    icon: 'text-orange-600',
    trend: 'text-orange-600',
  },
};

const MetricsCard = ({ title, value, unit, icon, trend, color, subtitle }: MetricsCardProps) => {
  const colors = colorClasses[color];

  const renderTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4" />;
      case 'down':
        return <TrendingDown className="w-4 h-4" />;
      case 'stable':
        return <Minus className="w-4 h-4" />;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0 overflow-hidden">
          <p className="text-sm font-medium text-gray-600 mb-1 truncate">{title}</p>
          <div className="flex items-baseline gap-1 flex-wrap">
            <span className="text-xl sm:text-3xl font-semibold text-gray-900 break-words">{value}</span>
            <span className="text-xs sm:text-sm text-gray-500 whitespace-nowrap">{unit}</span>
          </div>
          {subtitle && (
            <p className="text-xs text-amber-600 mt-1 font-medium truncate">{subtitle}</p>
          )}
        </div>
        <div className={`${colors.bg} p-2 sm:p-3 rounded-lg flex-shrink-0 self-start`}>
          <div className={colors.icon}>{icon}</div>
        </div>
      </div>
      <div className={`flex items-center gap-1 mt-3 sm:mt-4 ${colors.trend}`}>
        {renderTrendIcon()}
        <span className="text-xs font-medium capitalize">{trend}</span>
      </div>
    </div>
  );
};

export default MetricsCard;
