import React, { useState } from 'react';
import api from '../services/api';
import SectionHeader from '../components/SectionHeader';
import ExportButton from '../components/ExportButton';
import { useToast } from '../context/ToastContext';

const ReportsCenter = () => {
  const { showToast } = useToast();
  const [pdfLoading, setPdfLoading] = useState(false);
  const [excelLoading, setExcelLoading] = useState(false);

  const downloadFile = async (endpoint, filename, setLoading, formatName) => {
    setLoading(true);
    showToast(`Generating and downloading your ${formatName}...`, 'info');
    try {
      const res = await api.get(endpoint, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
      showToast(`${formatName} downloaded successfully!`, 'success');
    } catch (err) {
      console.error('Download failed:', err);
      showToast(`Failed to generate ${formatName}. Ensure statement files exist.`, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <SectionHeader 
        title="Reports Export Center" 
        subtitle="Generate executive summary PDF reports or download analytical Excel workbooks."
      />

      <div className="max-w-2xl mx-auto rounded-xl border border-slate-200 bg-white p-6 md:p-8 text-left shadow-xs space-y-6">
        <div>
          <h3 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-3 mb-4">Available Formats</h3>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {/* PDF Export card */}
          <div className="rounded-xl border border-slate-150 bg-slate-50 p-5 flex flex-col justify-between h-full">
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide">Executive PDF Summary</h4>
              <p className="text-[11px] leading-relaxed text-slate-500">
                Perfect for executive briefings. Includes KPI cards, expense splits, flagged budget anomalies, and cash flow runways.
              </p>
            </div>
            
            <ExportButton
              label="Export PDF"
              variant="pdf"
              isLoading={pdfLoading}
              onClick={() => downloadFile('/export-pdf', 'financial_report.pdf', setPdfLoading, 'Executive PDF Report')}
              className="mt-6 w-full"
            />
          </div>

          {/* Excel Export card */}
          <div className="rounded-xl border border-slate-150 bg-slate-50 p-5 flex flex-col justify-between h-full">
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide">Analytical Excel Workbook</h4>
              <p className="text-[11px] leading-relaxed text-slate-500">
                Perfect for detailed spreadsheets. Includes separate sheets for Transactions ledger, OCR Invoices list, Health score metrics, and Tax summaries.
              </p>
            </div>

            <ExportButton
              label="Export Excel"
              variant="excel"
              isLoading={excelLoading}
              onClick={() => downloadFile('/export-excel', 'financial_report.xlsx', setExcelLoading, 'Analytical Excel Workbook')}
              className="mt-6 w-full"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportsCenter;
