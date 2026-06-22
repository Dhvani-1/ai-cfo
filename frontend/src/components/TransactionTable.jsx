import React from 'react';

const TransactionTable = ({
  transactions = [],
  sortField,
  sortDirection,
  onSort
}) => {
  const headers = [
    { label: 'Date', field: 'date' },
    { label: 'Description', field: 'description' },
    { label: 'Amount', field: 'amount' },
    { label: 'Category', field: 'category' },
    { label: 'Type', field: 'type' }
  ];

  const renderSortArrow = (field) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? (
      <svg className="h-3 w-3 inline ml-1 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 15l7-7 7 7" />
      </svg>
    ) : (
      <svg className="h-3 w-3 inline ml-1 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 9l-7 7-7-7" />
      </svg>
    );
  };

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-xs select-none">
      <table className="min-w-full divide-y divide-slate-200 text-left text-xs text-slate-500">
        <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-700">
          <tr>
            {headers.map((h) => (
              <th
                key={h.field}
                scope="col"
                onClick={() => onSort && onSort(h.field)}
                className="px-6 py-4 cursor-pointer hover:bg-slate-100 transition-colors whitespace-nowrap"
              >
                <div className="flex items-center">
                  <span>{h.label}</span>
                  {renderSortArrow(h.field)}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {transactions.length === 0 ? (
            <tr>
              <td colSpan={headers.length} className="px-6 py-12 text-center text-slate-450 italic">
                No transaction records matching criteria.
              </td>
            </tr>
          ) : (
            transactions.map((tx, idx) => (
              <tr key={tx.id || idx} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap text-slate-450">{tx.date || 'N/A'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-slate-900 font-bold max-w-xs truncate" title={tx.description}>
                  {tx.description}
                </td>
                <td
                  className={`px-6 py-4 whitespace-nowrap font-extrabold ${
                    tx.amount >= 0 ? 'text-emerald-600' : 'text-slate-800'
                  }`}
                >
                  {tx.amount >= 0
                    ? `+$${tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
                    : `-$${Math.abs(tx.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="inline-flex rounded-md bg-indigo-50 border border-indigo-100 px-2 py-0.5 text-[10px] font-bold text-indigo-700 uppercase">
                    {tx.category || 'Others'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`inline-flex rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase ${
                      tx.type === 'Income'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                        : 'bg-slate-50 text-slate-700 border border-slate-200'
                    }`}
                  >
                    {tx.type}
                  </span>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default TransactionTable;
