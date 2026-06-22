import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

const COLORS = ['#6366f1', '#f43f5e'];

const HealthRatioChart = ({ savingsRatio = 0, expenseRatio = 0 }) => {
  const chartData = [
    { name: 'Savings Ratio', value: Math.max(0, savingsRatio) },
    { name: 'Expense Ratio', value: Math.max(0, expenseRatio) }
  ].filter(x => x.value > 0);

  if (chartData.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-xs italic text-slate-400">
        No ratio indicators computed.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={80}
          paddingAngle={3}
          dataKey="value"
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
        <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default HealthRatioChart;
