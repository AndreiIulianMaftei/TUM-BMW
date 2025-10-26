"use client"

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts"

interface CostDistributionChartProps {
  costs: {
    development: number
    marketing: number
    operations: number
    infrastructure: number
    personnel: number
    other: number
  }
}

export default function CostDistributionChart({ costs }: CostDistributionChartProps) {
  const COLORS = {
    development: "#3b82f6",
    marketing: "#8b5cf6",
    operations: "#10b981",
    infrastructure: "#f59e0b",
    personnel: "#ef4444",
    other: "#64748b",
  }

  const data = Object.entries(costs).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
    fill: COLORS[name as keyof typeof COLORS],
  }))

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const renderLabel = (entry: any) => {
    const percent = ((entry.value / entry.payload.total) * 100).toFixed(0)
    return `${entry.name}: ${percent}%`
  }

  return (
    <div className="w-full h-96">
      <h3 className="text-lg font-semibold text-slate-800 mb-4 text-center">Cost Distribution</h3>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderLabel}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => formatCurrency(value)}
            contentStyle={{
              backgroundColor: "white",
              border: "1px solid #e2e8f0",
              borderRadius: "8px",
              padding: "8px",
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
