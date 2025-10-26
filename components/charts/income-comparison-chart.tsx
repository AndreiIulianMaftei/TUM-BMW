"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface IncomeComparisonChartProps {
  models: {
    Royalties: { yearly_revenue: Record<string, number>; yearly_profit: Record<string, number> }
    Subscription: { yearly_revenue: Record<string, number>; yearly_profit: Record<string, number> }
    "Single Buy": { yearly_revenue: Record<string, number>; yearly_profit: Record<string, number> }
  }
  metric: "revenue" | "profit"
}

export default function IncomeComparisonChart({ models, metric }: IncomeComparisonChartProps) {
  const years = Object.keys(models.Royalties[`yearly_${metric}`])

  const data = years.map((year) => ({
    year,
    Royalties: models.Royalties[`yearly_${metric}`][year],
    Subscription: models.Subscription[`yearly_${metric}`][year],
    "Single Buy": models["Single Buy"][`yearly_${metric}`][year],
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
      <h3 className="text-lg font-semibold text-slate-800 mb-4 text-center">
        Income Model Comparison - {metric.charAt(0).toUpperCase() + metric.slice(1)}
      </h3>
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
          <Bar dataKey="Royalties" fill="#3b82f6" radius={[8, 8, 0, 0]} />
          <Bar dataKey="Subscription" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
          <Bar dataKey="Single Buy" fill="#10b981" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
