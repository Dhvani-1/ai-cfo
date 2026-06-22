import React, { useState, useEffect } from 'react';
import api from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import SectionHeader from '../components/SectionHeader';
import ChartCard from '../components/ChartCard';
import InfoPanel from '../components/InfoPanel';
import MonthlyTrendChart from '../charts/MonthlyTrendChart';
import ForecastChart from '../charts/ForecastChart';

const ForecastCenter = () => {
  const [forecast, setForecast] = useState(null);
  const [trends, setTrends] = useState(null);
  const [runway, setRunway] = useState(null);
  const [series, setSeries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [fcRes, trendRes, runwayRes, seriesRes] = await Promise.all([
          api.get('/forecast'),
          api.get('/trend-analysis'),
          api.get('/cash-runway'),
          api.get('/monthly-series')
        ]);
        setForecast(fcRes.data);
        setTrends(trendRes.data);
        setRunway(runwayRes.data);
        setSeries(seriesRes.data);
      } catch (err) {
        console.error(err);
        setError('Failed to fetch forecasting data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="flex h-96 items-center justify-center"><LoadingSpinner /></div>;
  if (error) return <div className="rounded-xl bg-rose-50 p-6 text-center text-rose-600 font-semibold border border-rose-100">{error}</div>;

  const runwayContent = (
    <div className="space-y-4">
      <p className="text-xs">
        {runway.status === 'cashflow_positive'
          ? `Your business operations generate a positive cash flow. Estimated runway is infinite with current metrics.`
          : `Your business has a net burn of $${runway.net_burn.toFixed(2)}/month. Remaining runway: ${runway.months_remaining} Months.`}
      </p>
      <div className="grid grid-cols-2 gap-4 border-t border-slate-200/50 pt-4 sm:grid-cols-4">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider opacity-60">Current Balance</span>
          <p className="text-sm font-bold text-slate-800">${runway.current_balance?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
        </div>
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider opacity-60">Avg Monthly Income</span>
          <p className="text-sm font-bold text-slate-800">${runway.average_monthly_income?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
        </div>
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider opacity-60">Avg Monthly Expenses</span>
          <p className="text-sm font-bold text-slate-800">${runway.average_monthly_expenses?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
        </div>
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider opacity-60">Net Burn Rate</span>
          <p className="text-sm font-bold text-slate-800">${runway.net_burn?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      <SectionHeader 
        title="Automated Forecasting Center" 
        subtitle="Linear regression trend classifications and moving average projections."
      />

      {/* Runway Banner Alert */}
      <InfoPanel 
        title={runway.status === 'cashflow_positive' ? 'Cashflow Positive Operations' : 'Active Capital Burn Run Rate'}
        content={runwayContent}
        type={runway.status === 'cashflow_positive' ? 'success' : 'warning'}
      />

      {/* Main Projections Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Side: Historical Cashflow Trends (Area) */}
        <div className="lg:col-span-2 flex flex-col">
          <ChartCard 
            title="Historical Cashflow Trends" 
            description="Comparative chronological timeline of inflows vs outflows"
            className="flex-1"
          >
            <MonthlyTrendChart data={series} />
          </ChartCard>
        </div>

        {/* Right Side: Moving Average Comparison (Bar) */}
        <div className="lg:col-span-1 flex flex-col">
          <ChartCard 
            title="Forecast Projections" 
            description="Comparing historical averages with projected moving averages"
            className="flex-1"
          >
            <ForecastChart 
              avgIncome={runway.average_monthly_income}
              avgExpense={runway.average_monthly_expenses}
              predIncome={forecast.predicted_income}
              predExpense={forecast.predicted_expenses}
            />
          </ChartCard>
        </div>
      </div>

      {/* Trend Slopes & Model Confidence */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Slopes */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left">
          <h3 className="text-sm font-bold text-slate-900">Regression Classification Slopes</h3>
          <p className="text-xs text-slate-400">Classified regression calculations (epsilon = 0.05)</p>
          
          <div className="mt-6 space-y-4">
            <div className="flex items-center justify-between rounded-lg bg-slate-50 p-3">
              <div>
                <p className="text-xs font-semibold text-slate-500">Income Trend</p>
                <p className="text-[10px] text-slate-400">Slope: {trends.income.slope?.toFixed(4)}</p>
              </div>
              <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-bold uppercase ${
                trends.income.trend === 'increasing' ? 'bg-emerald-50 text-emerald-700' :
                trends.income.trend === 'decreasing' ? 'bg-rose-50 text-rose-700' : 'bg-slate-100 text-slate-700'
              }`}>
                {trends.income.trend}
              </span>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-50 p-3">
              <div>
                <p className="text-xs font-semibold text-slate-500">Expense Trend</p>
                <p className="text-[10px] text-slate-400">Slope: {trends.expenses.slope?.toFixed(4)}</p>
              </div>
              <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-bold uppercase ${
                trends.expenses.trend === 'increasing' ? 'bg-rose-50 text-rose-700' :
                trends.expenses.trend === 'decreasing' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-700'
              }`}>
                {trends.expenses.trend === 'increasing' ? 'Increasing' : trends.expenses.trend === 'decreasing' ? 'Decreasing' : 'Stable'}
              </span>
            </div>
          </div>
        </div>

        {/* Confidence */}
        <div className="rounded-xl border border-slate-200 bg-indigo-900 p-6 shadow-xs text-left text-white flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-indigo-100">Model Forecasting Confidence</h3>
            <p className="text-xs text-indigo-300">Statistical forecasting reliability tier</p>
          </div>
          <div className="mt-6">
            <p className="text-3xl font-extrabold uppercase tracking-wide">{forecast.confidence}</p>
            <p className="mt-2 text-xs text-indigo-200 leading-relaxed">
              Confidence is derived from data volume. A minimum of 6 operational months yields medium reliability, while 12+ months provides high forecasting fidelity.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForecastCenter;
