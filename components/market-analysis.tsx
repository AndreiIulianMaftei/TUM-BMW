"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Loader2, TrendingUp, Users, Target } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LabelList,
} from "recharts"

interface MarketAnalysisProps {
  pdfText: string
  onComplete: (data: any) => void
}

export default function MarketAnalysis({ pdfText, onComplete }: MarketAnalysisProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [analysisData, setAnalysisData] = useState<any>(null)

  const handleGenerate = async () => {
    setIsGenerating(true)

    // Simulate API call
    setTimeout(() => {
      const mockData = {
        TAM: {
          description_of_public: "All BMW Motorrad owners globally",
          numbers: {
            "2024": 500000,
            "2025": 525000,
            "2026": 551250,
            "2027": 578813,
            "2028": 607753,
            "2029": 638141,
            "2030": 670048,
          },
        },
        SAM: {
          description_of_public: "BMW Motorrad owners in target markets",
          numbers: {
            "2024": 250000,
            "2025": 262500,
            "2026": 275625,
            "2027": 289406,
            "2028": 303876,
            "2029": 319070,
            "2030": 335024,
          },
        },
        SOM: {
          description_of_public: "Reachable customers in first 3 years",
          numbers: {
            "2024": 50000,
            "2025": 60000,
            "2026": 72000,
            "2027": 86400,
            "2028": 103680,
            "2029": 124416,
            "2030": 149299,
          },
        },
      }

      setAnalysisData(mockData)
      setIsGenerating(false)
    }, 3000)
  }

  const handleContinue = () => {
    onComplete(analysisData)
  }

  // Prepare chart data
  const growthData = analysisData
    ? Object.keys(analysisData.TAM.numbers).map((year) => ({
        year,
        TAM: analysisData.TAM.numbers[year],
        SAM: analysisData.SAM.numbers[year],
        SOM: analysisData.SOM.numbers[year],
      }))
    : []

  const funnelData = analysisData
    ? [
        { name: "TAM", value: analysisData.TAM.numbers["2024"], fill: "#3b82f6" },
        { name: "SAM", value: analysisData.SAM.numbers["2024"], fill: "#10b981" },
        { name: "SOM", value: analysisData.SOM.numbers["2024"], fill: "#f59e0b" },
      ]
    : []

  return (
    <div className="max-w-7xl mx-auto">
      {!analysisData ? (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="bg-white/80 backdrop-blur-sm shadow-xl">
            <CardHeader className="text-center">
              <CardTitle className="text-3xl">Generate Market Analysis</CardTitle>
              <CardDescription className="text-lg">
                AI will analyze your document and create TAM/SAM/SOM projections
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col items-center gap-6 py-12">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
                <TrendingUp className="w-10 h-10 text-blue-600" />
              </div>
              <Button
                onClick={handleGenerate}
                disabled={isGenerating}
                size="lg"
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-lg"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Analyzing Market Data...
                  </>
                ) : (
                  "Generate Analysis"
                )}
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      ) : (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
          {/* Summary Cards */}
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { label: "TAM 2024", value: analysisData.TAM.numbers["2024"], icon: Users, color: "blue" },
              { label: "SAM 2024", value: analysisData.SAM.numbers["2024"], icon: Target, color: "green" },
              { label: "SOM 2024", value: analysisData.SOM.numbers["2024"], icon: TrendingUp, color: "orange" },
            ].map((item, index) => {
              const Icon = item.icon
              return (
                <motion.div
                  key={item.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="bg-white shadow-lg hover:shadow-xl transition-shadow">
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-slate-600 font-medium">{item.label}</p>
                          <p className="text-3xl font-bold mt-2">{item.value.toLocaleString()}</p>
                        </div>
                        <div className={`w-14 h-14 bg-${item.color}-100 rounded-xl flex items-center justify-center`}>
                          <Icon className={`w-7 h-7 text-${item.color}-600`} />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )
            })}
          </div>

          {/* Charts */}
          <Card className="bg-white shadow-xl">
            <CardHeader>
              <CardTitle>Market Projections</CardTitle>
              <CardDescription>TAM/SAM/SOM growth from 2024-2030</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="growth" className="w-full">
                <TabsList className="grid w-full max-w-md mx-auto grid-cols-2">
                  <TabsTrigger value="growth">Growth Trend</TabsTrigger>
                  <TabsTrigger value="funnel">Market Funnel</TabsTrigger>
                </TabsList>

                <TabsContent value="growth" className="mt-6">
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={growthData}>
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
                      <Line
                        type="monotone"
                        dataKey="TAM"
                        stroke="#3b82f6"
                        strokeWidth={3}
                        dot={{ fill: "#3b82f6", r: 5 }}
                        activeDot={{ r: 7 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="SAM"
                        stroke="#10b981"
                        strokeWidth={3}
                        dot={{ fill: "#10b981", r: 5 }}
                        activeDot={{ r: 7 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="SOM"
                        stroke="#f59e0b"
                        strokeWidth={3}
                        dot={{ fill: "#f59e0b", r: 5 }}
                        activeDot={{ r: 7 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </TabsContent>

                <TabsContent value="funnel" className="mt-6">
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={funnelData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis type="number" stroke="#64748b" />
                      <YAxis dataKey="name" type="category" stroke="#64748b" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "white",
                          border: "1px solid #e2e8f0",
                          borderRadius: "8px",
                        }}
                      />
                      <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                        <LabelList
                          dataKey="value"
                          position="right"
                          formatter={(value: number) => value.toLocaleString()}
                        />
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Continue Button */}
          <div className="flex justify-center">
            <Button
              onClick={handleContinue}
              size="lg"
              className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 shadow-lg"
            >
              Continue to Cost Analysis
            </Button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
