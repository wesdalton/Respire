import { type ReactNode } from 'react';
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
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 md:p-5 xl:p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2 md:gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-xs md:text-sm font-medium text-gray-600 mb-1.5 md:mb-2 truncate">{title}</p>
          <div className="flex items-baseline gap-1 md:gap-1.5">
            <span className="text-2xl md:text-3xl xl:text-4xl font-bold text-gray-900 leading-none">{value}</span>
            <span className="text-sm md:text-base xl:text-lg text-gray-500 font-medium">{unit}</span>
          </div>
          {subtitle && (
            <p className="text-xs text-amber-600 mt-1.5 md:mt-2 font-medium truncate">{subtitle}</p>
          )}
        </div>
        <div className={`${colors.bg} p-2 md:p-3 xl:p-4 rounded-xl flex-shrink-0`}>
          <div className={`${colors.icon} flex items-center justify-center`}>
            <div className="w-5 h-5 md:w-6 md:h-6 xl:w-8 xl:h-8 [&>svg]:w-full [&>svg]:h-full">
              {icon}
            </div>
          </div>
        </div>
      </div>
      <div className={`flex items-center gap-1.5 mt-3 md:mt-4 ${colors.trend}`}>
        {renderTrendIcon()}
        <span className="text-xs font-medium capitalize">{trend}</span>
      </div>
    </div>
  );
};

export default MetricsCard;
