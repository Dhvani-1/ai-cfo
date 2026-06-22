import React, { useState, useEffect } from 'react';
import api from '../services/api';
import SectionHeader from '../components/SectionHeader';
import SearchBar from '../components/SearchBar';
import InvoiceTable from '../components/InvoiceTable';
import ConfirmationModal from '../components/ConfirmationModal';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { useToast } from '../context/ToastContext';
import { useNavigate } from 'react-router-dom';

const InvoicesPage = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Search filtering state
  const [searchQuery, setSearchQuery] = useState('');

  // Delete modal state
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState(null);

  // Selected invoice for detailed view
  const [selectedInvoice, setSelectedInvoice] = useState(null);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      const res = await api.get('/invoices');
      setInvoices(res.data);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch invoice ledger.');
    } finally {
      setLoading(false);
    }
  };

  const triggerDeletePrompt = (id) => {
    setDeleteTargetId(id);
    setIsDeleteOpen(true);
  };

  const executeDelete = async () => {
    if (!deleteTargetId) return;
    try {
      await api.delete(`/invoice/${deleteTargetId}`);
      setInvoices((prev) => prev.filter((inv) => inv.id !== deleteTargetId));
      showToast('Invoice deleted successfully.', 'success');
      
      // If deleted invoice is currently selected in details, reset details state
      if (selectedInvoice && selectedInvoice.id === deleteTargetId) {
        setSelectedInvoice(null);
      }
    } catch (err) {
      console.error(err);
      showToast('Failed to delete the requested invoice.', 'error');
    } finally {
      setDeleteTargetId(null);
    }
  };

  // Filter invoices based on Search Query (matches vendor, invoice number, category)
  const filteredInvoices = invoices.filter((inv) => {
    const vendorMatch = inv.vendor?.toLowerCase().includes(searchQuery.toLowerCase());
    const numberMatch = inv.invoice_number?.toLowerCase().includes(searchQuery.toLowerCase());
    const categoryMatch = inv.category?.toLowerCase().includes(searchQuery.toLowerCase());
    return vendorMatch || numberMatch || categoryMatch;
  });

  if (loading) return <div className="flex h-96 items-center justify-center"><LoadingSpinner /></div>;
  if (error) return <div className="rounded-xl bg-rose-50 p-6 text-center text-rose-600 font-semibold border border-rose-100">{error}</div>;

  return (
    <div className="space-y-6">
      <SectionHeader 
        title="OCR Invoices" 
        subtitle="Parsed invoices and receipts showing vendors, total amount, categories, and tax."
      />

      {invoices.length === 0 ? (
        <EmptyState
          title="No parsed invoices found"
          message="There are no processed invoice PDFs or images in your account. Drag-and-drop receipt files to parse Vendor, Totals, and GST parameters."
          actionLabel="Go to Upload Center"
          onAction={() => navigate('/upload')}
        />
      ) : (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3 items-start">
          {/* Invoices List Section */}
          <div className="xl:col-span-2 space-y-4">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="Search by vendor, number, or category..."
            />

            <InvoiceTable
              invoices={filteredInvoices}
              onDelete={triggerDeletePrompt}
              onViewDetails={setSelectedInvoice}
            />
          </div>

          {/* Selected Invoice Details Section (Right Column Panel) */}
          <div className="xl:col-span-1">
            {selectedInvoice ? (
              <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left animate-slide-in space-y-4">
                <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-805">Invoice Metadata</h3>
                  <button
                    onClick={() => setSelectedInvoice(null)}
                    className="text-slate-400 hover:text-slate-650"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-3.5 text-xs">
                  <div>
                    <span className="font-semibold text-slate-400">Vendor / Supplier</span>
                    <p className="mt-0.5 font-bold text-slate-850 text-sm">{selectedInvoice.vendor || 'N/A'}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="font-semibold text-slate-400">Invoice Number</span>
                      <p className="mt-0.5 font-bold text-slate-800">{selectedInvoice.invoice_number || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="font-semibold text-slate-400">Date</span>
                      <p className="mt-0.5 font-bold text-slate-800">{selectedInvoice.invoice_date || 'N/A'}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="font-semibold text-slate-400">Total Amount</span>
                      <p className="mt-0.5 font-extrabold text-indigo-650 text-sm">
                        ${selectedInvoice.total_amount?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </p>
                    </div>
                    <div>
                      <span className="font-semibold text-slate-400">Category</span>
                      <p className="mt-0.5 font-bold text-slate-800 uppercase">{selectedInvoice.category || 'N/A'}</p>
                    </div>
                  </div>
                  {selectedInvoice.gst_number && (
                    <div>
                      <span className="font-semibold text-slate-400">GST Registration Number</span>
                      <p className="mt-0.5 font-mono text-slate-800 tracking-wider font-bold">{selectedInvoice.gst_number}</p>
                    </div>
                  )}

                  {selectedInvoice.ocr_text && (
                    <div className="border-t border-slate-100 pt-3">
                      <span className="font-semibold text-slate-400">Extracted Raw Text</span>
                      <div className="mt-1.5 max-h-48 overflow-y-auto rounded-lg bg-slate-50 p-2.5 font-mono text-[9px] text-slate-600 border border-slate-150 leading-relaxed whitespace-pre-wrap">
                        {selectedInvoice.ocr_text}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="rounded-xl border border-slate-200 border-dashed bg-slate-50/50 p-12 text-center text-slate-400 italic text-xs">
                Select an invoice row from the ledger to display extracted OCR metadata and full page raw text details.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={executeDelete}
        title="Delete Invoice"
        message="Are you sure you want to delete this invoice? The record will be permanently removed from your accounting history."
        confirmLabel="Confirm Delete"
        cancelLabel="Discard"
      />
    </div>
  );
};

export default InvoicesPage;
