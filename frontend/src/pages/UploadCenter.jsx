import React, { useState } from 'react';
import api from '../services/api';
import SectionHeader from '../components/SectionHeader';
import FileUploadCard from '../components/FileUploadCard';
import { useToast } from '../context/ToastContext';

const UploadCenter = () => {
  const { showToast } = useToast();
  
  // Transaction Statement States
  const [txFile, setTxFile] = useState(null);
  const [txStatus, setTxStatus] = useState(null);
  const [txLoading, setTxLoading] = useState(false);

  // Invoice States
  const [invFile, setInvFile] = useState(null);
  const [invStatus, setInvStatus] = useState(null);
  const [invLoading, setInvLoading] = useState(false);
  const [parsedInvoice, setParsedInvoice] = useState(null);

  const handleTxUpload = async () => {
    if (!txFile) return;
    setTxLoading(true);
    setTxStatus(null);
    
    const formData = new FormData();
    formData.append('file', txFile);

    try {
      const res = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const msg = res.data.message || 'Transactions Statement uploaded and categorized successfully!';
      setTxStatus({ type: 'success', message: msg });
      showToast(msg, 'success');
      setTxFile(null);
    } catch (err) {
      console.error(err);
      const errMsg = err.response?.data?.detail || 'Transaction Statement upload failed. Verify spreadsheet format.';
      setTxStatus({ type: 'error', message: errMsg });
      showToast(errMsg, 'error');
    } finally {
      setTxLoading(false);
    }
  };

  const handleInvUpload = async () => {
    if (!invFile) return;
    setInvLoading(true);
    setInvStatus(null);
    setParsedInvoice(null);
    
    const formData = new FormData();
    formData.append('file', invFile);

    try {
      const res = await api.post('/upload-invoice', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (res.data.duplicate) {
        const warnMsg = `Invoice duplicate detected: ${res.data.message || 'Already exists'}`;
        setInvStatus({ type: 'warning', message: warnMsg });
        showToast(warnMsg, 'warning');
      } else {
        const successMsg = `Invoice parsed: ${res.data.vendor || 'N/A'} - $${res.data.total_amount || 0}`;
        setInvStatus({ type: 'success', message: successMsg });
        showToast(successMsg, 'success');
        setParsedInvoice(res.data);
      }
      setInvFile(null);
    } catch (err) {
      console.error(err);
      const errMsg = err.response?.data?.detail || 'Invoice processing failed. Ensure file is a readable PDF or Image.';
      setInvStatus({ type: 'error', message: errMsg });
      showToast(errMsg, 'error');
    } finally {
      setInvLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <SectionHeader 
        title="Upload Center" 
        subtitle="Ingest transaction statement spreadsheets or scan invoices via OCR."
      />

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Transaction Upload Card */}
        <FileUploadCard
          title="Upload Transaction Statement"
          description="Supports CSV and Excel spreadsheets containing dates, descriptions, and amounts."
          allowedTypesLabel="Select CSV (.csv) or Excel (.xlsx) Statement"
          accept=".csv, .xlsx"
          selectedFile={txFile}
          onFileSelect={setTxFile}
          onUpload={handleTxUpload}
          isLoading={txLoading}
          uploadStatus={txStatus}
        />

        {/* Invoice Upload Card */}
        <FileUploadCard
          title="Upload Invoice (OCR)"
          description="Supports PDF, PNG, JPG, JPEG, and TXT files. System will auto-extract totals, tax, and category."
          allowedTypesLabel="Select Invoice PDF or Image"
          accept=".pdf, .png, .jpg, .jpeg, .txt"
          selectedFile={invFile}
          onFileSelect={setInvFile}
          onUpload={handleInvUpload}
          isLoading={invLoading}
          uploadStatus={invStatus}
        />
      </div>

      {/* Extracted Invoice Details Block */}
      {parsedInvoice && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left animate-slide-in">
          <div className="border-b border-slate-100 pb-3 mb-4 flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">Extracted OCR Invoice Details</h3>
            <span className="inline-flex rounded-full bg-emerald-50 border border-emerald-100 px-2 py-0.5 text-[9px] font-bold text-emerald-700 uppercase">
              Parsed successfully
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-5 text-xs">
            <div className="rounded-lg bg-slate-50 p-3">
              <span className="font-semibold text-slate-400">Vendor</span>
              <p className="mt-1 font-bold text-slate-800 truncate" title={parsedInvoice.vendor}>{parsedInvoice.vendor || 'N/A'}</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-3">
              <span className="font-semibold text-slate-400">Invoice Number</span>
              <p className="mt-1 font-bold text-slate-800 truncate">{parsedInvoice.invoice_number || 'N/A'}</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-3">
              <span className="font-semibold text-slate-400">Invoice Date</span>
              <p className="mt-1 font-bold text-slate-800">{parsedInvoice.invoice_date || 'N/A'}</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-3">
              <span className="font-semibold text-slate-400">Total Amount</span>
              <p className="mt-1 font-bold text-indigo-700 font-extrabold">
                ${parsedInvoice.total_amount?.toLocaleString(undefined, { minimumFractionDigits: 2 }) || '0.00'}
              </p>
            </div>
            <div className="rounded-lg bg-slate-50 p-3">
              <span className="font-semibold text-slate-400">Category Assigned</span>
              <p className="mt-1 font-bold text-slate-800 uppercase truncate">{parsedInvoice.category || 'N/A'}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadCenter;
