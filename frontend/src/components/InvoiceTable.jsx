import React from 'react';

const InvoiceTable = ({ invoices = [], onDelete, onViewDetails }) => {
  const headers = ['Vendor', 'Invoice No', 'Date', 'Amount', 'Category', 'GST Details', 'Actions'];

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-xs select-none">
      <table className="min-w-full divide-y divide-slate-200 text-left text-xs text-slate-500">
        <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-700">
          <tr>
            {headers.map((h, i) => (
              <th key={i} scope="col" className="px-6 py-4">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {invoices.length === 0 ? (
            <tr>
              <td colSpan={headers.length} className="px-6 py-12 text-center text-slate-450 italic">
                No invoices found. Go to the Upload Center to process statements.
              </td>
            </tr>
          ) : (
            invoices.map((inv, idx) => (
              <tr key={inv.id || idx} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap text-slate-900 font-bold max-w-xs truncate" title={inv.vendor}>
                  {inv.vendor || 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap font-semibold text-slate-600">{inv.invoice_number || 'N/A'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-slate-450">{inv.invoice_date || 'N/A'}</td>
                <td className="px-6 py-4 whitespace-nowrap font-extrabold text-slate-900">
                  {inv.total_amount ? `$${inv.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="inline-flex rounded-md bg-indigo-50 border border-indigo-100 px-2 py-0.5 text-[10px] font-bold text-indigo-700 uppercase">
                    {inv.category || 'Others'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-slate-500 font-mono text-[10px] tracking-wide">
                  {inv.gst_number || 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-left text-xs font-semibold space-x-2">
                  {onViewDetails && (
                    <button
                      onClick={() => onViewDetails(inv)}
                      className="rounded-lg bg-indigo-50 border border-indigo-100 px-2.5 py-1 text-[10px] font-bold text-indigo-600 hover:bg-indigo-100 transition-colors cursor-pointer"
                    >
                      View details
                    </button>
                  )}
                  {onDelete && (
                    <button
                      onClick={() => onDelete(inv.id)}
                      className="rounded-lg bg-rose-50 border border-rose-100 px-2.5 py-1 text-[10px] font-bold text-rose-600 hover:bg-rose-100 transition-colors cursor-pointer"
                    >
                      Delete
                    </button>
                  )}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default InvoiceTable;
