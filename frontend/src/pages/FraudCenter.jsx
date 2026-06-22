import React, { useState, useEffect } from 'react';
import api from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import SectionHeader from '../components/SectionHeader';
import ChartCard from '../components/ChartCard';
import DataTable from '../components/DataTable';
import SeverityBadge from '../components/SeverityBadge';
import FraudPieChart from '../charts/FraudPieChart';

const FraudCenter = () => {
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFraudData = async () => {
      try {
        const [sumRes, alertsRes] = await Promise.all([
          api.get('/fraud-summary'),
          api.get('/fraud-alerts')
        ]);
        setSummary(sumRes.data);
        setAlerts(alertsRes.data);
      } catch (err) {
        console.error(err);
        setError('Failed to fetch fraud analysis.');
      } finally {
        setLoading(false);
      }
    };
    fetchFraudData();
  }, []);

  if (loading) return <div className="flex h-96 items-center justify-center"><LoadingSpinner /></div>;
  if (error) return <div className="rounded-xl bg-rose-50 p-6 text-center text-rose-600 font-semibold border border-rose-100">{error}</div>;

  const headers = ['Tx ID', 'Date', 'Description', 'Amount', 'Sources', 'Fraud Score', 'Severity'];

  const renderRow = (alert, idx) => (
    <tr key={idx} className="hover:bg-slate-50 text-left">
      <td className="px-6 py-4 whitespace-nowrap text-slate-500 font-semibold">#{alert.transaction_id}</td>
      <td className="px-6 py-4 whitespace-nowrap text-slate-500">{alert.date}</td>
      <td className="px-6 py-4 whitespace-nowrap">
        <p className="text-xs font-bold text-slate-805">{alert.description}</p>
        <p className="text-[10px] text-slate-400 max-w-xs truncate" title={alert.reasons?.join('; ')}>{alert.reasons?.join('; ')}</p>
      </td>
      <td className="px-6 py-4 whitespace-nowrap font-bold text-rose-650">${Math.abs(alert.amount).toFixed(2)}</td>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex flex-wrap gap-1">
          {alert.sources.map((s, i) => (
            <span key={i} className="inline-flex rounded-md bg-indigo-50 px-2 py-0.5 text-[9px] font-bold text-indigo-700 border border-indigo-105 uppercase tracking-wide">
              {s.replace('_', ' ')}
            </span>
          ))}
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap font-extrabold text-slate-800">{alert.fraud_score} / 100</td>
      <td className="px-6 py-4 whitespace-nowrap">
        <SeverityBadge severity={alert.severity} />
      </td>
    </tr>
  );

  return (
    <div className="space-y-8">
      <SectionHeader 
        title="Fraud & Outlier Audit Center" 
        subtitle="Unsupervised machine learning isolation forest pipelines and rule-based detectors."
      />

      {/* Alert Summary Banner */}
      <div className={`rounded-xl border p-6 text-left transition-all ${
        summary.total_alerts > 0
          ? 'border-amber-200 bg-amber-50 text-amber-900'
          : 'border-emerald-200 bg-emerald-50 text-emerald-900'
      }`}>
        <h2 className="text-base font-bold">
          {summary.total_alerts > 0
            ? `${summary.total_alerts} Suspicious Ledger Anomalies Flagged`
            : 'No Suspicious Transactions Labeled'}
        </h2>
        <p className="mt-1 text-xs opacity-90 leading-relaxed max-w-2xl">
          {summary.total_alerts > 0
            ? 'The CFO pipeline detects rapid transaction duplicates, abnormal outflow amounts, and multi-sourced outliers. Review the flagged records below.'
            : 'Operational ledger checks indicate all entries align with standard baseline behavior profiles. Zero exceptions triggered.'}
        </p>
      </div>

      {/* Stats and Pie Chart Row */}
      {summary.total_alerts > 0 && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Summary Stats Left Columns */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left lg:col-span-2 flex flex-col justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-4 mb-4">Risk Aggregations</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-lg bg-slate-50 p-4">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase">Flagged Entries</span>
                  <p className="mt-1 text-xl font-bold text-slate-850">{summary.total_alerts}</p>
                </div>
                <div className="rounded-lg bg-slate-50 p-4">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase">Average Risk Score</span>
                  <p className="mt-1 text-xl font-bold text-slate-850">{summary.average_fraud_score} / 100</p>
                </div>
                <div className="rounded-lg bg-slate-50 p-4">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase">Highest Risk Score</span>
                  <p className="mt-1 text-xl font-bold text-rose-650">{summary.highest_fraud_score} / 100</p>
                </div>
                <div className="rounded-lg bg-slate-50 p-4">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase">Highest Risk ID</span>
                  <p className="mt-1 text-xl font-bold text-slate-850">
                    {summary.highest_risk_transaction_id ? `#${summary.highest_risk_transaction_id}` : 'None'}
                  </p>
                </div>
              </div>
            </div>
            <p className="text-[10px] text-slate-400 mt-4 leading-relaxed">
              * Score calculation matches weights: duplicates (+40), absolute amounts (+20), repeating velocities (+15), and model confidence.
            </p>
          </div>

          {/* Pie Chart Right Column */}
          <div className="flex flex-col">
            <ChartCard 
              title="Alert Severity Ratios" 
              description="Distribution of triggered exceptions by severity tier"
              className="flex-1"
            >
              <FraudPieChart 
                critical={summary.high_severity}
                warning={summary.medium_severity}
                info={summary.low_severity}
              />
            </ChartCard>
          </div>
        </div>
      )}

      {/* Flagged Anomalies List */}
      <div className="space-y-4 text-left">
        <h3 className="text-sm font-bold text-slate-900">Audit Ledger List</h3>
        <DataTable
          headers={headers}
          data={alerts}
          renderRow={renderRow}
          emptyMessage="No anomalies found. Everything matches baseline transaction records."
        />
      </div>
    </div>
  );
};

export default FraudCenter;
