import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

const COLORS = ['#6366f1', '#ec4899', '#f59e0b', '#10b981', '#ef4444', '#64748b'];

const CategoryPieChart = ({ data = {} }) => {
  const chartData = Object.entries(data).map(([name, value]) => ({
    name,
    value
  }));

  if (chartData.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-xs italic text-slate-400">
        No category metrics available.
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
        <Tooltip formatter={(value) => `$${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} />
        <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default CategoryPieChart;
