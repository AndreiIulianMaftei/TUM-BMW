"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Loader2, DollarSign } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface CostAnalysisProps {
  pdfText: string
  marketData: any
  onComplete: (data: any) => void
}

export default function CostAnalysis({ pdfText, marketData, onComplete }: CostAnalysisProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [costData, setCostData] = useState<any>(null)

  const handleGenerate = async () => {
    setIsGenerating(true)

    setTimeout(() => {
      const mockData = {
        total_development_cost: 500000,
        total_customer_acquisition_cost: 150000,
        total_distribution_operations_cost: 100000,
        total_after_sales_cost: 75000,
        average_cogs_per_bundle: 45,
        yearly_cost_breakdown: {
          "2024": { total_cost: 950000, total_cogs: 2250000 },
          "2025": { total_cost: 325000, total_cogs: 2700000 },
          "2026": { total_cost: 325000, total_cogs: 3240000 },
          "2027": { total_cost: 325000, total_cogs: 3888000 },
          "2028": { total_cost: 325000, total_cogs: 4665600 },
          "2029": { total_cost: 325000, total_cogs: 5598720 },
          "2030": { total_cost: 325000, total_cogs: 6718464 },
        },
      }

      setCostData(mockData)
      setIsGenerating(false)
    }, 3000)
  }

  const chartData = costData
    ? Object.keys(costData.yearly_cost_breakdown).map((year) => ({
        year,
        "Fixed Costs": costData.yearly_cost_breakdown[year].total_cost,
        COGS: costData.yearly_cost_breakdown[year].total_cogs,
      }))
    : []

  return (
    <div className="max-w-7xl mx-auto">
      {!costData ? (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="bg-white/80 backdrop-blur-sm shadow-xl">
            <CardHeader className="text-center">
              <CardTitle className="text-3xl">Generate Cost Analysis</CardTitle>
              <CardDescription className="text-lg">
                Comprehensive breakdown of development, operations, and COGS
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col items-center gap-6 py-12">
              <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center">
                <DollarSign className="w-10 h-10 text-orange-600" />
              </div>
              <Button
                onClick={handleGenerate}
                disabled={isGenerating}
                size="lg"
                className="bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 shadow-lg"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Analyzing Costs...
                  </>
                ) : (
                  "Generate Cost Analysis"
                )}
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      ) : (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
          {/* Cost Summary Cards */}
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { label: "Development", value: costData.total_development_cost },
              { label: "Customer Acquisition", value: costData.total_customer_acquisition_cost },
              { label: "Distribution", value: costData.total_distribution_operations_cost },
              { label: "COGS per Unit", value: costData.average_cogs_per_bundle },
            ].map((item, index) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="bg-white shadow-lg">
                  <CardContent className="pt-6">
                    <p className="text-sm text-slate-600 font-medium">{item.label}</p>
                    <p className="text-2xl font-bold mt-2">€{item.value.toLocaleString()}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* Cost Chart */}
          <Card className="bg-white shadow-xl">
            <CardHeader>
              <CardTitle>Yearly Cost Breakdown</CardTitle>
              <CardDescription>Fixed costs and COGS over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="year" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "white",
                      border: "1px solid #e2e8f0",
                      borderRadius: "8px",
                    }}
                  />
                  <Legend />
                  <Bar dataKey="Fixed Costs" fill="#f59e0b" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="COGS" fill="#ef4444" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="flex justify-center">
            <Button
              onClick={() => onComplete(costData)}
              size="lg"
              className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 shadow-lg"
            >
              Continue to Income Analysis
            </Button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
