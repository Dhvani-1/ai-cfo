import React, { useState, useEffect } from 'react';
import api from '../services/api';
import SectionHeader from '../components/SectionHeader';
import ChartCard from '../components/ChartCard';
import DataTable from '../components/DataTable';
import LoadingSpinner from '../components/LoadingSpinner';
import CategoryPieChart from '../charts/CategoryPieChart';
import MonthlyTrendChart from '../charts/MonthlyTrendChart';
import InfoPanel from '../components/InfoPanel';
import RecommendationCard from '../components/RecommendationCard';

const InsightsPage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [monthlySummary, setMonthlySummary] = useState({});
  const [topExpenses, setTopExpenses] = useState([]);
  const [topIncome, setTopIncome] = useState([]);
  const [categoryRanking, setCategoryRanking] = useState({ total_expenses: 0, categories: [] });
  const [anomalies, setAnomalies] = useState([]);
  const [insightsData, setInsightsData] = useState({ financial_status: '', largest_category: '', largest_category_percentage: 0, insights: [] });

  useEffect(() => {
    const fetchInsightsData = async () => {
      try {
        const [
          summaryRes,
          expensesRes,
          incomeRes,
          rankingRes,
          anomaliesRes,
          insightsRes
        ] = await Promise.all([
          api.get('/monthly-summary'),
          api.get('/top-expenses?limit=5'),
          api.get('/top-income?limit=5'),
          api.get('/category-ranking'),
          api.get('/anomalies'),
          api.get('/insights')
        ]);

        setMonthlySummary(summaryRes.data);
        setTopExpenses(expensesRes.data);
        setTopIncome(incomeRes.data);
        setCategoryRanking(rankingRes.data);
        setAnomalies(anomaliesRes.data);
        setInsightsData(insightsRes.data);
      } catch (err) {
        console.error(err);
        setError('Failed to fetch financial insights data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchInsightsData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl bg-rose-50 p-6 text-center text-rose-600 font-semibold border border-rose-100">
        {error}
      </div>
    );
  }

  // Format Monthly Summary for MonthlyTrendChart (expects array of { month, income, expenses })
  const trendData = Object.entries(monthlySummary).map(([month, val]) => ({
    month,
    income: val.income,
    expenses: val.expenses
  })).sort((a, b) => a.month.localeCompare(b.month));

  // Format Category Ranking for CategoryPieChart (expects object of { categoryName: amount })
  const pieChartData = {};
  categoryRanking.categories.forEach(cat => {
    pieChartData[cat.category] = cat.amount;
  });

  return (
    <div className="space-y-8">
      <SectionHeader 
        title="Financial Insights" 
        subtitle="Chronological trends, transaction anomalies, and smart CFO observations."
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left">
          <span className="text-xs font-semibold text-slate-400 uppercase">Operational Status</span>
          <p className="mt-2 text-xl font-bold text-slate-800 capitalize">
            {insightsData.financial_status ? insightsData.financial_status.replace('_', ' ') : 'Stable'}
          </p>
          <p className="text-[10px] text-slate-400">Calculated based on recent net savings</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left">
          <span className="text-xs font-semibold text-slate-400 uppercase">Largest Spending Sector</span>
          <p className="mt-2 text-xl font-bold text-slate-800 uppercase">
            {insightsData.largest_category || 'N/A'}
          </p>
          <p className="text-[10px] text-slate-400">
            Accounting for {insightsData.largest_category_percentage?.toFixed(1)}% of total outflows
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs text-left">
          <span className="text-xs font-semibold text-slate-400 uppercase">Total Outflows Analyzed</span>
          <p className="mt-2 text-xl font-bold text-indigo-600">
            ${categoryRanking.total_expenses?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </p>
          <p className="text-[10px] text-slate-400">Sum of all categorizable expenses</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <ChartCard title="Monthly Cashflow Trends" description="Comparative timeline of revenues vs operational costs">
          <MonthlyTrendChart data={trendData} />
        </ChartCard>

        <ChartCard title="Category Cost Distribution" description="Relative share of expenses by labeled categories">
          <CategoryPieChart data={pieChartData} />
        </ChartCard>
      </div>

      {/* CFO Recommendation / Insights Row */}
      {insightsData.insights && insightsData.insights.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-left text-sm font-bold text-slate-900">CFO Core Recommendations</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {insightsData.insights.map((insight, idx) => (
              <RecommendationCard 
                key={idx}
                category="Insight"
                message={insight}
                severity={idx % 2 === 0 ? 'warning' : 'info'}
                priority={idx + 1}
              />
            ))}
          </div>
        </div>
      )}

      {/* Top Ledger Items (Income & Expenses side-by-side) */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Top Income Ledger */}
        <div className="space-y-4 text-left">
          <h3 className="text-sm font-bold text-slate-900">Top Income Inflows</h3>
          <DataTable 
            headers={['Date', 'Description', 'Category', 'Amount']}
            data={topIncome}
            renderRow={(row, idx) => (
              <tr key={idx} className="hover:bg-slate-50">
                <td className="px-6 py-4 whitespace-nowrap text-slate-550">{row.date}</td>
                <td className="px-6 py-4 whitespace-nowrap text-slate-900 font-semibold">{row.description}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="inline-flex rounded-md bg-indigo-50 px-2 py-0.5 text-[10px] font-bold text-indigo-700 uppercase">
                    {row.category}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-emerald-600 font-bold">
                  +${row.amount?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </td>
              </tr>
            )}
            emptyMessage="No income transactions recorded."
          />
        </div>

        {/* Top Expense Outflows */}
        <div className="space-y-4 text-left">
          <h3 className="text-sm font-bold text-slate-900">Top Expense Outflows</h3>
          <DataTable 
            headers={['Date', 'Description', 'Category', 'Amount']}
            data={topExpenses}
            renderRow={(row, idx) => (
              <tr key={idx} className="hover:bg-slate-50">
                <td className="px-6 py-4 whitespace-nowrap text-slate-550">{row.date}</td>
                <td className="px-6 py-4 whitespace-nowrap text-slate-900 font-semibold">{row.description}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="inline-flex rounded-md bg-rose-50 px-2 py-0.5 text-[10px] font-bold text-rose-700 uppercase">
                    {row.category}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-rose-600 font-bold">
                  -${Math.abs(row.amount)?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </td>
              </tr>
            )}
            emptyMessage="No expense transactions recorded."
          />
        </div>
      </div>

      {/* Anomalies and Outliers */}
      <div className="space-y-4 text-left">
        <h3 className="text-sm font-bold text-slate-900">Flagged Budget Anomalies</h3>
        <p className="text-xs text-slate-400">Transactions exceeding normal standard category deviation thresholds</p>
        <DataTable 
          headers={['Description', 'Category Outflow', 'Allowed Category Threshold', 'Excess Deviation']}
          data={anomalies}
          renderRow={(row, idx) => (
            <tr key={idx} className="hover:bg-slate-50">
              <td className="px-6 py-4 whitespace-nowrap text-slate-900 font-semibold">{row.description}</td>
              <td className="px-6 py-4 whitespace-nowrap text-rose-600 font-bold">${Math.abs(row.amount)?.toFixed(2)}</td>
              <td className="px-6 py-4 whitespace-nowrap text-slate-500">${row.threshold?.toFixed(2)}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="inline-flex rounded-full bg-rose-100 px-2.5 py-0.5 text-xs font-bold text-rose-800">
                  +${row.deviation?.toFixed(2)} Excess
                </span>
              </td>
            </tr>
          )}
          emptyMessage="No category budget deviations detected. Operations match limits."
        />
      </div>
    </div>
  );
};

export default InsightsPage;
