import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from 'recharts';

const IncomeExpenseBarChart = ({ income = 0, expenses = 0 }) => {
  const chartData = [
    { name: 'Income', value: income, color: '#6366f1' },
    { name: 'Expenses', value: expenses, color: '#f43f5e' }
  ];

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
        <YAxis stroke="#94a3b8" fontSize={11} />
        <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

export default IncomeExpenseBarChart;
