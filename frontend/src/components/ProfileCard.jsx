import React from 'react';

const ProfileCard = ({ user, totalIncome = 0, totalExpenses = 0 }) => {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left select-none space-y-6">
      <div className="flex flex-col items-center text-center space-y-3">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-indigo-100 text-2xl font-extrabold text-indigo-600 border border-indigo-200">
          {user?.name ? user.name[0].toUpperCase() : 'U'}
        </div>
        <div>
          <h2 className="text-base font-bold text-slate-900 leading-none">{user?.name || 'Executive User'}</h2>
          <p className="text-[10px] text-slate-400 font-semibold mt-1">Company Administrator</p>
        </div>
      </div>

      <div className="border-t border-slate-100 pt-6 space-y-4 text-xs font-medium text-slate-600">
        <div className="flex justify-between items-center border-b border-slate-50 pb-2">
          <span className="text-slate-400">Email address</span>
          <span className="text-slate-800 font-bold max-w-[150px] truncate" title={user?.email}>{user?.email}</span>
        </div>
        <div className="flex justify-between items-center border-b border-slate-50 pb-2">
          <span className="text-slate-400">Member since</span>
          <span className="text-slate-800 font-bold">
            {user?.created_at ? new Date(user.created_at).toLocaleDateString(undefined, { dateStyle: 'medium' }) : 'N/A'}
          </span>
        </div>
        <div className="flex justify-between items-center border-b border-slate-50 pb-2">
          <span className="text-slate-400">Transactions processed</span>
          <span className="text-slate-800 font-bold">{user?.statistics?.transactions || 0} items</span>
        </div>
        <div className="flex justify-between items-center border-b border-slate-50 pb-2">
          <span className="text-slate-400">Registered invoices</span>
          <span className="text-slate-800 font-bold">{user?.statistics?.invoices || 0} items</span>
        </div>
        <div className="flex justify-between items-center border-b border-slate-50 pb-2">
          <span className="text-slate-400">Accumulated income</span>
          <span className="text-emerald-600 font-extrabold">
            ${totalIncome.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-400">Accumulated expenses</span>
          <span className="text-rose-600 font-extrabold">
            ${totalExpenses.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </span>
        </div>
      </div>
    </div>
  );
};

export default ProfileCard;
