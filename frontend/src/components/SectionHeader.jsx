import React from 'react';

const SectionHeader = ({ title, subtitle, actions }) => {
  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between text-left">
      <div>
        <h2 className="text-lg font-bold text-slate-900 leading-none">{title}</h2>
        {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </div>
  );
};

export default SectionHeader;
