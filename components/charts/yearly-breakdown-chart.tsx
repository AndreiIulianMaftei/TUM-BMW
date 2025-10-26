"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface YearlyBreakdownChartProps {
  yearlyData: Record<
    string,
    {
      development: number
      marketing: number
      operations: number
      infrastructure: number
      personnel: number
      other: number
    }
  >
}

export default function YearlyBreakdownChart({ yearlyData }: YearlyBreakdownChartProps) {
  const data = Object.entries(yearlyData).map(([year, costs]) => ({
    year,
    ...costs,
  }))

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
      notation: "compact",
    }).format(value)
  }

  return (
    <div className="w-full h-96">
      <h3 className="text-lg font-semibold text-slate-800 mb-4 text-center">Yearly Cost Breakdown</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="year" stroke="#64748b" />
          <YAxis tickFormatter={formatCurrency} stroke="#64748b" />
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
          <Bar dataKey="development" stackId="a" fill="#3b82f6" />
          <Bar dataKey="marketing" stackId="a" fill="#8b5cf6" />
          <Bar dataKey="operations" stackId="a" fill="#10b981" />
          <Bar dataKey="infrastructure" stackId="a" fill="#f59e0b" />
          <Bar dataKey="personnel" stackId="a" fill="#ef4444" />
          <Bar dataKey="other" stackId="a" fill="#64748b" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
