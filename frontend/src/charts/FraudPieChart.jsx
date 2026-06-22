import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

const COLORS = ['#ef4444', '#f59e0b', '#64748b'];

const FraudPieChart = ({ critical = 0, warning = 0, info = 0 }) => {
  const chartData = [
    { name: 'Critical/High', value: critical },
    { name: 'Warning/Medium', value: warning },
    { name: 'Low/Info', value: info }
  ].filter(x => x.value > 0);

  if (chartData.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-xs italic text-slate-400">
        No fraud alerts logged.
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
        <Tooltip formatter={(value) => `${value} Alerts`} />
        <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default FraudPieChart;
