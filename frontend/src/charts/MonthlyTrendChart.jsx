import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const MonthlyTrendChart = ({ data = [] }) => {
  if (data.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-xs italic text-slate-400">
        No monthly trends available.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
        <defs>
          <linearGradient id="trendIncomeColor" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.15}/>
            <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="trendExpenseColor" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.15}/>
            <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} />
        <YAxis stroke="#94a3b8" fontSize={11} />
        <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
        <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
        <Area type="monotone" name="Income" dataKey="income" stroke="#6366f1" fillOpacity={1} fill="url(#trendIncomeColor)" />
        <Area type="monotone" name="Expenses" dataKey="expenses" stroke="#f43f5e" fillOpacity={1} fill="url(#trendExpenseColor)" />
      </AreaChart>
    </ResponsiveContainer>
  );
};

export default MonthlyTrendChart;
