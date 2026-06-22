import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const ForecastChart = ({ avgIncome = 0, avgExpense = 0, predIncome = 0, predExpense = 0 }) => {
  const chartData = [
    {
      name: 'Historical Average',
      Income: avgIncome,
      Expenses: avgExpense
    },
    {
      name: 'Moving Average Forecast',
      Income: predIncome,
      Expenses: predExpense
    }
  ];

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={chartData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
        <YAxis stroke="#94a3b8" fontSize={11} />
        <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
        <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
        <Bar dataKey="Income" fill="#6366f1" radius={[4, 4, 0, 0]} />
        <Bar dataKey="Expenses" fill="#f43f5e" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default ForecastChart;
