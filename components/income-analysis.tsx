"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Loader2, DollarSign, Percent, CreditCard } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts"

interface IncomeAnalysisProps {
  pdfText: string
  marketData: any
  costData: any
  onComplete: (data: any) => void
}

export default function IncomeAnalysis({ pdfText, marketData, costData, onComplete }: IncomeAnalysisProps) {
  const [selectedModel, setSelectedModel] = useState<"royalties" | "subscription" | "single" | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [incomeData, setIncomeData] = useState<any>(null)

  const handleGenerate = async (model: "royalties" | "subscription" | "single") => {
    setSelectedModel(model)
    setIsGenerating(true)

    setTimeout(() => {
      const mockData = {
        model,
        total_income: 15000000,
        yearly_projections: [
          { year: 2024, yearly_income: 1500000 },
          { year: 2025, yearly_income: 1800000 },
          { year: 2026, yearly_income: 2160000 },
          { year: 2027, yearly_income: 2592000 },
          { year: 2028, yearly_income: 3110400 },
          { year: 2029, yearly_income: 3732480 },
          { year: 2030, yearly_income: 4478976 },
        ],
      }

      setIncomeData(mockData)
      setIsGenerating(false)
      onComplete(mockData)
    }, 3000)
  }

  // Calculate profit data
  const profitData =
    incomeData && costData
      ? incomeData.yearly_projections.map((proj: any) => {
          const yearCosts = costData.yearly_cost_breakdown[proj.year]
          const totalCost = yearCosts ? yearCosts.total_cost + yearCosts.total_cogs : 0
          return {
            year: proj.year,
            Income: proj.yearly_income,
            Costs: totalCost,
            Profit: proj.yearly_income - totalCost,
          }
        })
      : []

  const cumulativeData = profitData.reduce((acc: any[], curr: any, index: number) => {
    const cumulative = index === 0 ? curr.Profit : acc[index - 1].Cumulative + curr.Profit
    return [...acc, { ...curr, Cumulative: cumulative }]
  }, [])

  const totalProfit = profitData.reduce((sum: number, item: any) => sum + item.Profit, 0)
  const totalIncome = profitData.reduce((sum: number, item: any) => sum + item.Income, 0)
  const totalCosts = profitData.reduce((sum: number, item: any) => sum + item.Costs, 0)
  const profitMargin = totalIncome > 0 ? (totalProfit / totalIncome) * 100 : 0

  return (
    <div className="max-w-7xl mx-auto">
      {!incomeData ? (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <Card className="bg-white/80 backdrop-blur-sm shadow-xl">
            <CardHeader className="text-center">
              <CardTitle className="text-3xl">Select Income Strategy</CardTitle>
              <CardDescription className="text-lg">
                Choose your revenue model to generate income projections
              </CardDescription>
            </CardHeader>
            <CardContent className="py-8">
              <div className="grid md:grid-cols-3 gap-6">
                {[
                  {
                    id: "royalties",
                    title: "Royalties Model",
                    description: "Percentage-based revenue per sale",
                    icon: Percent,
                    color: "blue",
                  },
                  {
                    id: "subscription",
                    title: "Subscription Model",
                    description: "Recurring monthly revenue",
                    icon: CreditCard,
                    color: "purple",
                  },
                  {
                    id: "single",
                    title: "One-Time Sale",
                    description: "Single purchase per customer",
                    icon: DollarSign,
                    color: "green",
                  },
                ].map((model) => {
                  const Icon = model.icon
                  return (
                    <motion.div key={model.id} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Card
                        className={`cursor-pointer transition-all hover:shadow-xl ${
                          selectedModel === model.id ? "ring-2 ring-blue-500" : ""
                        }`}
                        onClick={() => !isGenerating && handleGenerate(model.id as any)}
                      >
                        <CardContent className="pt-6 text-center">
                          <div
                            className={`w-16 h-16 bg-${model.color}-100 rounded-full flex items-center justify-center mx-auto mb-4`}
                          >
                            <Icon className={`w-8 h-8 text-${model.color}-600`} />
                          </div>
                          <h3 className="font-semibold text-lg mb-2">{model.title}</h3>
                          <p className="text-sm text-slate-600">{model.description}</p>
                          {isGenerating && selectedModel === model.id && (
                            <div className="mt-4">
                              <Loader2 className="w-6 h-6 animate-spin mx-auto text-blue-600" />
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </motion.div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ) : (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
          {/* Profit Summary */}
          <div
            className={`rounded-xl p-8 ${totalProfit > 0 ? "bg-gradient-to-r from-green-500 to-emerald-600" : "bg-gradient-to-r from-red-500 to-rose-600"} text-white shadow-2xl`}
          >
            <div className="grid md:grid-cols-4 gap-6">
              <div>
                <p className="text-green-100 text-sm font-medium mb-1">Total Income</p>
                <p className="text-3xl font-bold">€{totalIncome.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-green-100 text-sm font-medium mb-1">Total Costs</p>
                <p className="text-3xl font-bold">€{totalCosts.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-green-100 text-sm font-medium mb-1">Net Profit</p>
                <p className="text-3xl font-bold">€{totalProfit.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-green-100 text-sm font-medium mb-1">Profit Margin</p>
                <p className="text-3xl font-bold">{profitMargin.toFixed(1)}%</p>
              </div>
            </div>
          </div>

          {/* Charts */}
          <Card className="bg-white shadow-xl">
            <CardHeader>
              <CardTitle>Financial Projections</CardTitle>
              <CardDescription>Income, costs, and profit analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="comparison" className="w-full">
                <TabsList className="grid w-full max-w-md mx-auto grid-cols-2">
                  <TabsTrigger value="comparison">Income vs Costs</TabsTrigger>
                  <TabsTrigger value="cumulative">Cumulative Profit</TabsTrigger>
                </TabsList>

                <TabsContent value="comparison" className="mt-6">
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={profitData}>
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
                      <Bar dataKey="Income" fill="#10b981" radius={[8, 8, 0, 0]} />
                      <Bar dataKey="Costs" fill="#ef4444" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </TabsContent>

                <TabsContent value="cumulative" className="mt-6">
                  <ResponsiveContainer width="100%" height={400}>
                    <AreaChart data={cumulativeData}>
                      <defs>
                        <linearGradient id="colorCumulative" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1} />
                        </linearGradient>
                      </defs>
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
                      <Area
                        type="monotone"
                        dataKey="Cumulative"
                        stroke="#8b5cf6"
                        strokeWidth={3}
                        fillOpacity={1}
                        fill="url(#colorCumulative)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex justify-center gap-4">
            <Button
              onClick={() => {
                setIncomeData(null)
                setSelectedModel(null)
              }}
              variant="outline"
              size="lg"
            >
              Try Different Model
            </Button>
            <Button
              onClick={() => {
                // Download or export functionality
                const dataStr = JSON.stringify({ marketData, costData, incomeData }, null, 2)
                const dataBlob = new Blob([dataStr], { type: "application/json" })
                const url = URL.createObjectURL(dataBlob)
                const link = document.createElement("a")
                link.href = url
                link.download = "analysis-results.json"
                link.click()
              }}
              size="lg"
              className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-lg"
            >
              Download Results
            </Button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
