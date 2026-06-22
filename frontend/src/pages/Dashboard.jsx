import React, { useState, useEffect } from 'react';
import api from '../services/api';
import StatCard from '../components/StatCard';
import LoadingSpinner from '../components/LoadingSpinner';
import SectionHeader from '../components/SectionHeader';
import ChartCard from '../components/ChartCard';
import RiskBadge from '../components/RiskBadge';
import CategoryPieChart from '../charts/CategoryPieChart';
import IncomeExpenseBarChart from '../charts/IncomeExpenseBarChart';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [health, setHealth] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashRes, healthRes, forecastRes] = await Promise.all([
          api.get('/dashboard'),
          api.get('/financial-health'),
          api.get('/forecast')
        ]);
        setData(dashRes.data);
        setHealth(healthRes.data);
        setForecast(forecastRes.data);
      } catch (err) {
        console.error(err);
        setError('Failed to fetch dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="flex h-96 items-center justify-center"><LoadingSpinner /></div>;
  if (error) return <div className="rounded-xl bg-rose-50 p-6 text-center text-rose-600 font-semibold border border-rose-100">{error}</div>;

  const { cashflow, profit_loss, categories } = data;

  return (
    <div className="space-y-8">
      <SectionHeader 
        title="Financial Executive Dashboard" 
        subtitle="Real-time KPI indicators, categorized cost centers, and automated forecasting runway."
      />

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Income"
          value={`$${profit_loss.revenue?.toLocaleString(undefined, { minimumFractionDigits: 2 }) || '0.00'}`}
          trend="Inflow Total"
          trendType="positive"
          icon={<svg className="h-6 w-6 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" /></svg>}
        />
        <StatCard
          title="Total Expenses"
          value={`$${profit_loss.expenses?.toLocaleString(undefined, { minimumFractionDigits: 2 }) || '0.00'}`}
          trend="Outflow Total"
          trendType="neutral"
          icon={<svg className="h-6 w-6 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 12H4" /></svg>}
        />
        <StatCard
          title="Net Cashflow"
          value={`$${cashflow.net_cashflow?.toLocaleString(undefined, { minimumFractionDigits: 2 }) || '0.00'}`}
          trend={cashflow.net_cashflow >= 0 ? 'Surplus' : 'Deficit'}
          trendType={cashflow.net_cashflow >= 0 ? 'positive' : 'negative'}
          icon={<svg className="h-6 w-6 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>}
        />
        <StatCard
          title="Financial Health Score"
          value={`${health.health_score.score} / 100`}
          trend={`Grade: ${health.grade.grade}`}
          trendType={health.health_score.score >= 70 ? 'positive' : health.health_score.score >= 50 ? 'neutral' : 'negative'}
          icon={<svg className="h-6 w-6 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>}
        />
      </div>

      {/* Main Charts & Runway section */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Section: Expense Category Distribution */}
        <div className="lg:col-span-1 flex flex-col h-full">
          <ChartCard 
            title="Expenses by Category" 
            description="Distribution of absolute expenses" 
            className="flex-1"
          >
            <CategoryPieChart data={categories} />
          </ChartCard>
        </div>

        {/* Middle Section: Income vs Expenses Bar Chart */}
        <div className="lg:col-span-1 flex flex-col h-full">
          <ChartCard 
            title="Income vs Expenses" 
            description="Total revenues versus outflows comparison" 
            className="flex-1"
          >
            <IncomeExpenseBarChart income={profit_loss.revenue} expenses={profit_loss.expenses} />
          </ChartCard>
        </div>

        {/* Right Section: Cash Burn & Forecasting Runway */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs lg:col-span-1 text-left flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-4 mb-4">Future Financial Projections</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg bg-slate-50 p-4">
                <span className="text-[10px] font-semibold text-slate-400 uppercase">Predicted Income</span>
                <p className="mt-1 text-base font-bold text-indigo-700">${forecast.predicted_income?.toFixed(2)}</p>
                <p className="text-[9px] text-slate-400">Moving average</p>
              </div>
              <div className="rounded-lg bg-slate-50 p-4">
                <span className="text-[10px] font-semibold text-slate-400 uppercase">Predicted Expenses</span>
                <p className="mt-1 text-base font-bold text-rose-600">${forecast.predicted_expenses?.toFixed(2)}</p>
                <p className="text-[9px] text-slate-400">Moving average</p>
              </div>
              <div className="rounded-lg bg-slate-50 p-4">
                <span className="text-[10px] font-semibold text-slate-400 uppercase">Runway Months</span>
                <p className="mt-1 text-base font-bold text-slate-800">
                  {forecast.months_remaining !== null ? `${forecast.months_remaining} Mos` : 'Infinite'}
                </p>
                <p className="text-[9px] text-slate-400">Runway status: {forecast.runway_status?.replace('_', ' ')}</p>
              </div>
              <div className="rounded-lg bg-indigo-600 p-4 text-white">
                <span className="text-[10px] font-semibold text-indigo-200 uppercase">Confidence</span>
                <p className="mt-1 text-base font-bold uppercase">{forecast.confidence}</p>
                <p className="text-[9px] text-indigo-200">Data history level</p>
              </div>
            </div>
          </div>
          
          <div className="mt-6 border-t border-slate-100 pt-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xs font-bold text-slate-800">Risk Assessment</h3>
                <p className="text-[10px] text-slate-400">Standard operating risk tier</p>
              </div>
              <RiskBadge riskLevel={health.risk.risk_level} />
            </div>
            <ul className="mt-4 space-y-1.5 text-xs text-slate-650">
              {health.risk.reasons.slice(0, 2).map((r, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-indigo-500 font-semibold">•</span>
                  <span className="truncate leading-relaxed">{r}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
