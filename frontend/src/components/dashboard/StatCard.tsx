import React from 'react';

interface StatCardProps {
  title: string;
  value: string;
  subValue?: string;
  subValueLabel?: string;
  icon?: string;
  trend?: string;
  trendLabel?: string;
  color?: 'primary' | 'white';
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subValueLabel,
  icon,
  trend,
  trendLabel,
  color = 'white',
}) => {
  const isPrimary = color === 'primary';

  if (isPrimary) {
    return (
      <div className="bg-gradient-to-br from-primary to-blue-600 rounded-2xl p-6 text-white shadow-lg shadow-blue-200/50 dark:shadow-none relative overflow-hidden group hover:-translate-y-1 transition-transform duration-300">
        <div className="absolute -right-6 -top-6 p-4 opacity-10 group-hover:opacity-20 transition-opacity duration-500">
          <span className="material-symbols-outlined text-9xl">{icon}</span>
        </div>
        <div className="relative z-10 flex flex-col h-full justify-between min-h-[140px]">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-blue-100 text-sm font-semibold">{title}</p>
              <h3 className="text-4xl font-bold mt-2 tracking-tight">{value}</h3>
            </div>
            <span className="bg-white/20 backdrop-blur-sm rounded-lg p-2 shadow-inner border border-white/10">
              <span className="material-symbols-outlined text-white">{icon}</span>
            </span>
          </div>
          {trend && (
            <div className="flex items-center gap-3 text-sm font-medium text-blue-50 mt-4">
              <span className="bg-white/20 px-2 py-1 rounded-md text-white flex items-center gap-1 backdrop-blur-md">
                <span className="material-symbols-outlined text-sm">trending_up</span> {trend}
              </span>
              <span className="opacity-80">{trendLabel}</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-md transition-all duration-300">
      <div className="flex justify-between items-start mb-4">
        <div className="p-2.5 bg-orange-50 dark:bg-orange-900/20 rounded-xl">
          <span className="material-symbols-outlined text-orange-500 text-[24px]">{icon}</span>
        </div>
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">{title}</span>
      </div>
      <div>
        <span className="text-3xl font-bold text-slate-900 dark:text-white">{value}</span>
        <p className="text-sm text-slate-500 mt-1 font-medium">{subValueLabel}</p>
      </div>
    </div>
  );
};

export default StatCard;
