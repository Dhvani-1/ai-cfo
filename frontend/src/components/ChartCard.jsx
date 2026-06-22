import React from 'react';

const ChartCard = ({ title, description, children, className = '' }) => {
  return (
    <div className={`rounded-xl border border-slate-200 bg-white p-6 shadow-xs ${className}`}>
      <div className="text-left border-b border-slate-100 pb-4 mb-4">
        <h3 className="text-sm font-bold text-slate-900">{title}</h3>
        {description && <p className="mt-0.5 text-xs text-slate-400">{description}</p>}
      </div>
      <div className="h-64">
        {children}
      </div>
    </div>
  );
};

export default ChartCard;
