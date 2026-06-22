import React from 'react';

const SeverityBadge = ({ severity }) => {
  const getStyle = () => {
    const s = severity?.toLowerCase();
    if (s === 'critical' || s === 'high') {
      return 'bg-rose-50 text-rose-700 border-rose-200';
    }
    if (s === 'warning' || s === 'medium') {
      return 'bg-amber-50 text-amber-750 border-amber-200';
    }
    return 'bg-slate-100 text-slate-700 border-slate-200';
  };

  return (
    <span className={`inline-flex rounded-full border px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider ${getStyle()}`}>
      {severity}
    </span>
  );
};

export default SeverityBadge;
