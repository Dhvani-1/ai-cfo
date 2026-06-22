import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Breadcrumbs = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  const routeNameMap = {
    dashboard: 'Dashboard',
    insights: 'Insights',
    forecast: 'Forecast Center',
    health: 'Health Center',
    fraud: 'Fraud Center',
    tax: 'Tax Center',
    upload: 'Upload Center',
    transactions: 'Transactions Ledger',
    invoices: 'OCR Invoices',
    chat: 'AI CFO Chat',
    reports: 'Reports Export',
    profile: 'My Profile'
  };

  if (pathnames.length === 0) return null;

  return (
    <nav className="flex text-xs font-semibold text-slate-400 mb-2 select-none" aria-label="Breadcrumb">
      <ol className="inline-flex items-center space-x-1.5 md:space-x-2">
        <li className="inline-flex items-center">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-1 hover:text-slate-650 transition-colors"
          >
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            CFO Platform
          </Link>
        </li>
        {pathnames.map((name, index) => {
          const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`;
          const isLast = index === pathnames.length - 1;
          const label = routeNameMap[name.toLowerCase()] || name;

          return (
            <li key={name} className="flex items-center">
              <svg className="h-3.5 w-3.5 text-slate-300 mx-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7" />
              </svg>
              {isLast ? (
                <span className="text-slate-600 font-bold max-w-[120px] sm:max-w-none truncate">{label}</span>
              ) : (
                <Link
                  to={routeTo}
                  className="hover:text-slate-650 transition-colors max-w-[120px] sm:max-w-none truncate"
                >
                  {label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
