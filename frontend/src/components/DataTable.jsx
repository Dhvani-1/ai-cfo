import React from 'react';

const DataTable = ({ headers, data, renderRow, emptyMessage = "No data available." }) => {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200 text-left text-sm text-slate-500">
        <thead className="bg-slate-50 text-xs font-semibold uppercase text-slate-700">
          <tr>
            {headers.map((h, i) => (
              <th key={i} scope="col" className="px-6 py-4">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {data.length === 0 ? (
            <tr>
              <td colSpan={headers.length} className="px-6 py-10 text-center text-slate-400 italic">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, idx) => (
              renderRow ? renderRow(row, idx) : (
                <tr key={idx} className="hover:bg-slate-50">
                  {Object.values(row).map((val, cellIdx) => (
                    <td key={cellIdx} className="px-6 py-4 whitespace-nowrap text-slate-900">
                      {val !== null && val !== undefined ? String(val) : '-'}
                    </td>
                  ))}
                </tr>
              )
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
