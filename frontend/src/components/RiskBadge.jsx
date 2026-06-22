import React from 'react';

const RiskBadge = ({ riskLevel }) => {
  const getStyle = () => {
    const r = riskLevel?.toLowerCase();
    if (r === 'high') return 'bg-rose-50 text-rose-700 border-rose-200';
    if (r === 'medium') return 'bg-amber-50 text-amber-750 border-amber-200';
    return 'bg-emerald-50 text-emerald-750 border-emerald-200';
  };

  return (
    <span className={`inline-flex rounded-full border px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider ${getStyle()}`}>
      {riskLevel} Risk
    </span>
  );
};

export default RiskBadge;
