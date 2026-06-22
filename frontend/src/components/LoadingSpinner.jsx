import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center justify-center space-y-2">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-indigo-600"></div>
      <p className="text-sm font-medium text-slate-500">Loading CFO Insights...</p>
    </div>
  );
};

export default LoadingSpinner;
