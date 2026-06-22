import React, { useState, useEffect } from 'react';
import api from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import SectionHeader from '../components/SectionHeader';
import InfoPanel from '../components/InfoPanel';
import RecommendationCard from '../components/RecommendationCard';

const TaxCenter = () => {
  const [taxData, setTaxData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTax = async () => {
      try {
        const res = await api.get('/tax-summary');
        setTaxData(res.data);
      } catch (err) {
        console.error(err);
        setError('Failed to load tax analysis.');
      } finally {
        setLoading(false);
      }
    };
    fetchTax();
  }, []);

  if (loading) return <div className="flex h-96 items-center justify-center"><LoadingSpinner /></div>;
  if (error) return <div className="rounded-xl bg-rose-50 p-6 text-center text-rose-600 font-semibold border border-rose-100">{error}</div>;

  const { gst, estimate, insights, disclaimer } = taxData;

  return (
    <div className="space-y-8">
      <SectionHeader 
        title="Tax Assessment & Deductions Center" 
        subtitle="GST extraction audits, taxable balance estimations, and automated deductible insights."
      />

      {/* Overview Taxable Income Card */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left">
        <h2 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-4 mb-4">Taxable Income Estimation</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="rounded-lg bg-slate-50 p-4">
            <span className="text-[10px] font-semibold text-slate-400 uppercase">Gross Income</span>
            <p className="mt-1 text-base font-bold text-slate-800">${estimate.income?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
          </div>
          <div className="rounded-lg bg-slate-50 p-4">
            <span className="text-[10px] font-semibold text-slate-400 uppercase">Deductions (Expenses)</span>
            <p className="mt-1 text-base font-bold text-slate-800">${estimate.expenses?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
          </div>
          <div className="rounded-lg bg-slate-50 p-4">
            <span className="text-[10px] font-semibold text-slate-400 uppercase">Taxable Balance</span>
            <p className="mt-1 text-base font-bold text-indigo-700">${estimate.taxable_income?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
          </div>
          <div className="rounded-lg bg-indigo-650 p-4 text-white">
            <span className="text-[10px] font-semibold text-indigo-200 uppercase">Deduction Ratio</span>
            <p className="mt-1 text-base font-bold">{estimate.expense_ratio}%</p>
          </div>
        </div>
      </div>

      {/* GST Summary & Insights */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* GST Card */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left">
          <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-4 mb-4">Goods and Services Tax (GST)</h3>
          
          <div className="space-y-4 text-sm text-slate-650">
            <div className="flex justify-between border-b border-slate-100 pb-2">
              <span>Total GST Paid</span>
              <strong className="text-slate-805">${gst.total_gst_paid?.toFixed(2)}</strong>
            </div>
            <div className="flex justify-between border-b border-slate-100 pb-2">
              <span>GST Invoices Processed</span>
              <span className="font-semibold text-slate-800">{gst.invoice_count}</span>
            </div>
            <div className="flex justify-between border-b border-slate-100 pb-2 text-xs">
              <span className="pl-4 text-slate-400">• Labeled Explicit GST</span>
              <span className="text-slate-700 font-semibold">{gst.explicit_gst_invoices}</span>
            </div>
            <div className="flex justify-between border-b border-slate-100 pb-2 text-xs">
              <span className="pl-4 text-slate-400">• Labeled Estimated GST (18%)</span>
              <span className="text-slate-705 font-semibold">{gst.estimated_gst_invoices}</span>
            </div>
            <div className="flex justify-between pt-1">
              <span>Average GST per Invoice</span>
              <strong className="text-slate-800">${gst.average_gst?.toFixed(2)}</strong>
            </div>
          </div>
        </div>

        {/* Insights Card */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-4 mb-4">Tax Deductions & Warnings</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between rounded-lg bg-slate-50 p-3 text-xs">
                <span className="font-semibold text-slate-550">Income Status</span>
                <span className={`inline-flex rounded-full px-2.5 py-0.5 font-bold uppercase tracking-wider text-[10px] ${
                  insights.tax_status === 'positive_income' ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 'bg-rose-50 text-rose-700 border border-rose-100'
                }`}>
                  {insights.tax_status?.replace('_', ' ')}
                </span>
              </div>
              {insights.largest_expense_category && (
                <div className="flex items-center justify-between rounded-lg bg-slate-50 p-3 text-xs">
                  <span className="font-semibold text-slate-550">Largest Deductible Sector</span>
                  <span className="font-bold text-slate-800 uppercase">{insights.largest_expense_category}</span>
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 border-t border-slate-100 pt-6">
            <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Analysis Log</h4>
            <ul className="mt-2 space-y-2 text-xs text-slate-650">
              {insights.insights?.map((ins, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-indigo-505 font-bold">•</span>
                  <span className="leading-relaxed">{ins}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Insights recommendations if relevant */}
      {insights.insights?.length > 0 && (
        <div className="space-y-4 text-left">
          <h3 className="text-sm font-bold text-slate-900">Suggested Action Plan</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {insights.insights.slice(0, 2).map((ins, idx) => (
              <RecommendationCard 
                key={idx}
                category="Tax Audit"
                message={ins}
                severity="info"
                priority={idx + 1}
              />
            ))}
          </div>
        </div>
      )}

      {/* Disclaimer InfoPanel */}
      <InfoPanel 
        title="Regulatory Compliance Disclaimer"
        content={disclaimer}
        type="info"
      />
    </div>
  );
};

export default TaxCenter;
