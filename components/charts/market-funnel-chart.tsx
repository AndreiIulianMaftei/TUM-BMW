"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"

interface MarketFunnelChartProps {
  tam: number
  sam: number
  som: number
  year: string
}

export default function MarketFunnelChart({ tam, sam, som, year }: MarketFunnelChartProps) {
  const data = [
    { name: "TAM", value: tam, fill: "#3b82f6" },
    { name: "SAM", value: sam, fill: "#10b981" },
    { name: "SOM", value: som, fill: "#f59e0b" },
  ]

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(0)}K`
    return num.toLocaleString()
  }

  return (
    <div className="w-full h-80">
      <h3 className="text-lg font-semibold text-slate-800 mb-4 text-center">Market Funnel - {year}</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 80, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis type="number" tickFormatter={formatNumber} stroke="#64748b" />
          <YAxis type="category" dataKey="name" stroke="#64748b" />
          <Tooltip
            formatter={(value: number) => formatNumber(value)}
            contentStyle={{
              backgroundColor: "white",
              border: "1px solid #e2e8f0",
              borderRadius: "8px",
              padding: "8px",
            }}
          />
          <Bar dataKey="value" radius={[0, 8, 8, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
