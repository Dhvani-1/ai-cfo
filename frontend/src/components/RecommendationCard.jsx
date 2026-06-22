import React from 'react';
import SeverityBadge from './SeverityBadge';

const RecommendationCard = ({ category, message, severity, priority }) => {
  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-xs hover:shadow-md transition-all text-left">
      <div className="space-y-1.5 pr-4">
        <div className="flex items-center gap-2">
          <span className="inline-flex rounded-full bg-indigo-50 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-indigo-600 border border-indigo-100">
            {category}
          </span>
          {priority && (
            <span className="text-[10px] text-slate-400 font-semibold">Priority #{priority}</span>
          )}
        </div>
        <p className="text-xs font-semibold text-slate-700 leading-relaxed">{message}</p>
      </div>
      <SeverityBadge severity={severity} />
    </div>
  );
};

export default RecommendationCard;
