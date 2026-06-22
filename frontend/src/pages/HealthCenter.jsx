import React, { useState, useEffect } from 'react';
import api from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import SectionHeader from '../components/SectionHeader';
import ChartCard from '../components/ChartCard';
import RiskBadge from '../components/RiskBadge';
import RecommendationCard from '../components/RecommendationCard';
import HealthRatioChart from '../charts/HealthRatioChart';

const HealthCenter = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await api.get('/financial-health');
        setHealth(res.data);
      } catch (err) {
        console.error(err);
        setError('Failed to load financial health report.');
      } finally {
        setLoading(false);
      }
    };
    fetchHealth();
  }, []);

  if (loading) return <div className="flex h-96 items-center justify-center"><LoadingSpinner /></div>;
  if (error) return <div className="rounded-xl bg-rose-50 p-6 text-center text-rose-600 font-semibold border border-rose-100">{error}</div>;

  const { health_score, grade, risk, ratios, recommendations } = health;

  const getGradeBg = (c) => {
    if (c === 'green') return 'border-emerald-200 bg-emerald-50 text-emerald-850';
    if (c === 'blue') return 'border-indigo-200 bg-indigo-50 text-indigo-850';
    if (c === 'yellow') return 'border-amber-200 bg-amber-50 text-amber-850';
    if (c === 'orange') return 'border-orange-200 bg-orange-50 text-orange-850';
    return 'border-rose-200 bg-rose-50 text-rose-850';
  };

  return (
    <div className="space-y-8">
      <SectionHeader 
        title="Financial Health & Audit Center" 
        subtitle="Automated weighted scoring, operational risk diagnostics, and CFO recommendations."
      />

      {/* Grade and Score Card */}
      <div className={`rounded-xl border p-6 text-left flex flex-col md:flex-row items-center justify-between gap-6 transition-all ${getGradeBg(grade.color)}`}>
        <div className="space-y-2">
          <h2 className="text-lg font-bold">Overall Health Rating: Grade {grade.grade} ({grade.description})</h2>
          <p className="text-xs leading-relaxed opacity-90">
            Your weighted health score is calculated at <b className="text-sm font-extrabold">{health_score.score}%</b>. 
            Optimizing savings rates, extending cash runway, and reducing anomaly frequencies will improve this grade.
          </p>
        </div>
        <div className="flex shrink-0 items-center justify-center h-20 w-20 rounded-full bg-white/40 border border-white/50 backdrop-blur-xs shadow-xs">
          <span className="text-3xl font-extrabold tracking-tight">{grade.grade}</span>
        </div>
      </div>

      {/* Ratios Breakdown with Pie Chart */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Progress Bar Indicators */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-4 mb-4">Key Operational Ratios</h3>
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
                  <span>Savings Ratio</span>
                  <span className="text-slate-800 font-bold">{ratios.savings_ratio}%</span>
                </div>
                <div className="mt-2 h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div className="h-full rounded-full bg-indigo-600 transition-all" style={{ width: `${Math.max(0, Math.min(100, ratios.savings_ratio))}%` }}></div>
                </div>
                <p className="mt-1.5 text-[9px] text-slate-400">Formula: ((Revenue - Expenses) / Revenue) * 100</p>
              </div>
              <div>
                <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
                  <span>Expense Ratio</span>
                  <span className="text-slate-800 font-bold">{ratios.expense_ratio}%</span>
                </div>
                <div className="mt-2 h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div className="h-full rounded-full bg-indigo-600 transition-all" style={{ width: `${Math.max(0, Math.min(100, ratios.expense_ratio))}%` }}></div>
                </div>
                <p className="mt-1.5 text-[9px] text-slate-400">Formula: (Expenses / Revenue) * 100</p>
              </div>
            </div>
          </div>
          <p className="text-[10px] text-slate-400 mt-4 leading-relaxed">
            * Healthy bounds specify a savings ratio greater than 20% and expense ratio below 80% to ensure active reinvestment capital.
          </p>
        </div>

        {/* Ratio Chart Wrapper */}
        <div className="flex flex-col">
          <ChartCard 
            title="Capital Efficiency Split" 
            description="Comparing savings share versus total expense allocation"
            className="flex-1"
          >
            <HealthRatioChart savingsRatio={ratios.savings_ratio} expenseRatio={ratios.expense_ratio} />
          </ChartCard>
        </div>
      </div>

      {/* Risk and Recommendations Section */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Risk Analysis Card (Left Column) */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left lg:col-span-1 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-4 mb-4">Risk Profile</h3>
            
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">Risk Severity score</span>
              <span className="text-sm font-bold text-slate-800">{risk.risk_score} / 100</span>
            </div>
            
            <div className="mt-6 flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">Current Assessment</span>
              <RiskBadge riskLevel={risk.risk_level} />
            </div>

            <div className="mt-6 border-t border-slate-100 pt-6">
              <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Risk Factors Indicated</h4>
              <ul className="mt-2.5 space-y-2 text-xs text-slate-650">
                {risk.reasons.map((reason, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-rose-500 font-bold">•</span>
                    <span className="leading-relaxed">{reason}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Recommendations list (Right Columns) */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left lg:col-span-2">
          <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-4 mb-4">Prioritized Action Items</h3>
          
          <div className="space-y-4 max-h-[360px] overflow-y-auto pr-1">
            {recommendations.length === 0 ? (
              <p className="text-xs text-slate-400 italic py-6 text-center">No high priority health warnings logged.</p>
            ) : (
              recommendations.map((rec, idx) => (
                <RecommendationCard 
                  key={idx}
                  category={rec.category}
                  message={rec.message}
                  severity={rec.severity}
                  priority={idx + 1}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HealthCenter;
