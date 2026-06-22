import React from 'react';

const StatCard = ({ title, value, trend, trendType, icon }) => {
  const getTrendColor = () => {
    if (trendType === 'positive') return 'text-emerald-600 bg-emerald-50';
    if (trendType === 'negative') return 'text-rose-600 bg-rose-50';
    return 'text-slate-600 bg-slate-50';
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs transition-all hover:shadow-md">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-500">{title}</span>
        {icon && <div className="text-slate-400">{icon}</div>}
      </div>
      <div className="mt-4 flex items-baseline justify-between">
        <span className="text-2xl font-bold text-slate-900">{value}</span>
        {trend && (
          <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold ${getTrendColor()}`}>
            {trend}
          </span>
        )}
      </div>
    </div>
  );
};

export default StatCard;
