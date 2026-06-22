import React from 'react';

const InfoPanel = ({ title, content, type = 'info' }) => {
  const getStyle = () => {
    if (type === 'success') return 'border-emerald-200 bg-emerald-50 text-emerald-800';
    if (type === 'warning') return 'border-amber-200 bg-amber-50 text-amber-805';
    if (type === 'error') return 'border-rose-200 bg-rose-50 text-rose-805';
    return 'border-indigo-200 bg-indigo-50 text-indigo-805';
  };

  return (
    <div className={`rounded-xl border p-5 text-left ${getStyle()}`}>
      {title && <h4 className="text-sm font-bold leading-none">{title}</h4>}
      <div className={`${title ? 'mt-2' : ''} text-xs leading-relaxed`}>{content}</div>
    </div>
  );
};

export default InfoPanel;
