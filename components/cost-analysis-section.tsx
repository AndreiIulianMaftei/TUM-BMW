"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { DollarSign, Edit3, Save, Loader2, PieChart, Plus, Trash2 } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface CostAnalysisSectionProps {
  pdfText: string
  marketData: any
  onDataChange: (data: any) => void
  costData: any
}

interface CostItem {
  name: string
  amount: number
  category: string
}

export default function CostAnalysisSection({ pdfText, marketData, onDataChange, costData }: CostAnalysisSectionProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [isEditMode, setIsEditMode] = useState(false)
  const [localData, setLocalData] = useState<any>(costData)

  useEffect(() => {
    if (costData) {
      setLocalData(costData)
    }
  }, [costData])

  const generateAnalysis = async () => {
    setIsGenerating(true)

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000))

    const years = Object.keys(marketData?.TAM?.numbers || {})
    const yearlyBreakdown: any = {}

    years.forEach((year, index) => {
      const growthFactor = 1 + index * 0.05
      yearlyBreakdown[year] = {
        development: Math.round(500000 * growthFactor),
        marketing: Math.round(300000 * growthFactor),
        operations: Math.round(200000 * growthFactor),
        infrastructure: Math.round(150000 * growthFactor),
        personnel: Math.round(400000 * growthFactor),
        other: Math.round(100000 * growthFactor),
      }
    })

    const mockData = {
      total_costs: {
        development: 500000,
        marketing: 300000,
        operations: 200000,
        infrastructure: 150000,
        personnel: 400000,
        other: 100000,
      },
      yearly_breakdown: yearlyBreakdown,
      cost_items: [
        { name: "Software Development", amount: 300000, category: "development" },
        { name: "Hardware & Equipment", amount: 200000, category: "development" },
        { name: "Digital Marketing", amount: 150000, category: "marketing" },
        { name: "Brand Partnerships", amount: 150000, category: "marketing" },
        { name: "Customer Support", amount: 100000, category: "operations" },
        { name: "Logistics & Fulfillment", amount: 100000, category: "operations" },
        { name: "Cloud Infrastructure", amount: 80000, category: "infrastructure" },
        { name: "Data Storage", amount: 70000, category: "infrastructure" },
        { name: "Engineering Team", amount: 250000, category: "personnel" },
        { name: "Sales Team", amount: 150000, category: "personnel" },
        { name: "Legal & Compliance", amount: 50000, category: "other" },
        { name: "Insurance", amount: 50000, category: "other" },
      ],
      justification:
        "Cost estimates based on industry benchmarks for premium automotive accessory platforms, including development, marketing, and operational expenses scaled to market size.",
      assumptions: [
        "Development costs include initial platform build and ongoing maintenance",
        "Marketing budget assumes 20% of projected first-year revenue",
        "Personnel costs based on competitive salaries for automotive tech sector",
        "Infrastructure scales with user growth projections",
      ],
    }

    setLocalData(mockData)
    onDataChange(mockData)
    setIsGenerating(false)
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const getTotalCost = () => {
    if (!localData?.total_costs) return 0
    return Object.values(localData.total_costs).reduce((sum: number, val: any) => sum + val, 0)
  }

  const getCategoryTotal = (category: string) => {
    if (!localData?.cost_items) return 0
    return localData.cost_items
      .filter((item: CostItem) => item.category === category)
      .reduce((sum: number, item: CostItem) => sum + item.amount, 0)
  }

  const updateCostCategory = (category: string, amount: number) => {
    const updated = { ...localData }
    updated.total_costs[category] = amount
    setLocalData(updated)
    onDataChange(updated)
  }

  const addCostItem = (category: string) => {
    const updated = { ...localData }
    updated.cost_items.push({
      name: "New Cost Item",
      amount: 0,
      category: category,
    })
    setLocalData(updated)
    onDataChange(updated)
  }

  const removeCostItem = (index: number) => {
    const updated = { ...localData }
    updated.cost_items.splice(index, 1)
    setLocalData(updated)
    onDataChange(updated)
  }

  const updateCostItem = (index: number, field: string, value: any) => {
    const updated = { ...localData }
    updated.cost_items[index][field] = value
    setLocalData(updated)
    onDataChange(updated)
  }

  if (!localData && !isGenerating) {
    return (
      <Card className="p-8 bg-white/80 backdrop-blur-sm border-green-200 shadow-lg">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
            <DollarSign className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800">Cost Analysis</h2>
            <p className="text-slate-600 text-sm">Generate comprehensive cost breakdown</p>
          </div>
        </div>

        <div className="text-center py-12">
          <p className="text-slate-600 mb-6">Generate detailed cost analysis based on market data</p>
          <Button onClick={generateAnalysis} size="lg" className="px-8 bg-green-600 hover:bg-green-700">
            <DollarSign className="w-5 h-5 mr-2" />
            Generate Cost Analysis
          </Button>
        </div>
      </Card>
    )
  }

  if (isGenerating) {
    return (
      <Card className="p-8 bg-white/80 backdrop-blur-sm border-green-200 shadow-lg">
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="w-16 h-16 text-green-600 animate-spin mb-4" />
          <p className="text-lg font-medium text-slate-700">Generating cost analysis with AI...</p>
          <p className="text-sm text-slate-500 mt-2">Calculating development, marketing, and operational costs</p>
        </div>
      </Card>
    )
  }

  const categories = [
    { key: "development", label: "Development", color: "blue" },
    { key: "marketing", label: "Marketing", color: "purple" },
    { key: "operations", label: "Operations", color: "green" },
    { key: "infrastructure", label: "Infrastructure", color: "amber" },
    { key: "personnel", label: "Personnel", color: "red" },
    { key: "other", label: "Other", color: "slate" },
  ]

  const years = Object.keys(localData?.yearly_breakdown || {})

  return (
    <Card className="p-8 bg-white/80 backdrop-blur-sm border-green-200 shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
            <DollarSign className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800">Cost Analysis</h2>
            <p className="text-slate-600 text-sm">Comprehensive Cost Breakdown</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant={isEditMode ? "default" : "outline"} size="sm" onClick={() => setIsEditMode(!isEditMode)}>
            {isEditMode ? <Save className="w-4 h-4 mr-2" /> : <Edit3 className="w-4 h-4 mr-2" />}
            {isEditMode ? "Save" : "Edit"}
          </Button>
          <Button variant="outline" size="sm" onClick={generateAnalysis}>
            Regenerate
          </Button>
        </div>
      </div>

      {/* Total Cost Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8 p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-xl border-2 border-green-200"
      >
        <p className="text-sm font-semibold text-green-600 uppercase tracking-wide mb-2">Total Estimated Costs</p>
        <p className="text-4xl font-bold text-green-900">{formatCurrency(getTotalCost())}</p>
        <p className="text-sm text-green-700 mt-2">First year operational costs</p>
      </motion.div>

      {/* Cost Categories Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        {categories.map((category) => (
          <motion.div
            key={category.key}
            whileHover={{ scale: 1.02 }}
            className={`p-4 bg-${category.color}-50 rounded-lg border border-${category.color}-200`}
          >
            <p className="text-xs font-semibold text-slate-600 uppercase tracking-wide mb-1">{category.label}</p>
            {isEditMode ? (
              <Input
                type="number"
                value={localData?.total_costs?.[category.key] || 0}
                onChange={(e) => updateCostCategory(category.key, Number(e.target.value))}
                className="text-lg font-bold mt-1"
              />
            ) : (
              <p className="text-xl font-bold text-slate-900">
                {formatCurrency(localData?.total_costs?.[category.key] || 0)}
              </p>
            )}
            <p className="text-xs text-slate-600 mt-1">
              {((localData?.total_costs?.[category.key] / getTotalCost()) * 100).toFixed(1)}% of total
            </p>
          </motion.div>
        ))}
      </div>

      {/* Detailed Cost Items */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">Detailed Cost Items</h3>
        <Tabs defaultValue="development" className="w-full">
          <TabsList className="grid w-full grid-cols-3 md:grid-cols-6">
            {categories.map((cat) => (
              <TabsTrigger key={cat.key} value={cat.key} className="text-xs">
                {cat.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {categories.map((category) => (
            <TabsContent key={category.key} value={category.key} className="space-y-3">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-slate-700">
                  Category Total: {formatCurrency(getCategoryTotal(category.key))}
                </p>
                {isEditMode && (
                  <Button size="sm" variant="outline" onClick={() => addCostItem(category.key)}>
                    <Plus className="w-4 h-4 mr-1" />
                    Add Item
                  </Button>
                )}
              </div>

              <div className="space-y-2">
                {localData?.cost_items
                  ?.filter((item: CostItem) => item.category === category.key)
                  .map((item: CostItem, index: number) => {
                    const globalIndex = localData.cost_items.indexOf(item)
                    return (
                      <div key={globalIndex} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                        {isEditMode ? (
                          <>
                            <Input
                              value={item.name}
                              onChange={(e) => updateCostItem(globalIndex, "name", e.target.value)}
                              className="flex-1 text-sm"
                              placeholder="Cost item name"
                            />
                            <Input
                              type="number"
                              value={item.amount}
                              onChange={(e) => updateCostItem(globalIndex, "amount", Number(e.target.value))}
                              className="w-32 text-sm"
                              placeholder="Amount"
                            />
                            <Button size="sm" variant="ghost" onClick={() => removeCostItem(globalIndex)}>
                              <Trash2 className="w-4 h-4 text-red-600" />
                            </Button>
                          </>
                        ) : (
                          <>
                            <p className="flex-1 text-sm text-slate-700">{item.name}</p>
                            <p className="text-sm font-semibold text-slate-900">{formatCurrency(item.amount)}</p>
                          </>
                        )}
                      </div>
                    )
                  })}
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </div>

      {/* Yearly Breakdown */}
      {years.length > 0 && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Yearly Cost Projections</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-4 font-semibold text-slate-700">Category</th>
                  {years.map((year) => (
                    <th key={year} className="text-right py-3 px-4 font-semibold text-slate-700">
                      {year}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {categories.map((category) => (
                  <tr key={category.key} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-3 px-4 font-medium text-slate-700">{category.label}</td>
                    {years.map((year) => (
                      <td key={year} className="text-right py-3 px-4 text-slate-600">
                        {formatCurrency(localData?.yearly_breakdown?.[year]?.[category.key] || 0)}
                      </td>
                    ))}
                  </tr>
                ))}
                <tr className="bg-slate-100 font-semibold">
                  <td className="py-3 px-4 text-slate-900">Total</td>
                  {years.map((year) => {
                    const yearTotal = Object.values(localData?.yearly_breakdown?.[year] || {}).reduce(
                      (sum: number, val: any) => sum + val,
                      0,
                    )
                    return (
                      <td key={year} className="text-right py-3 px-4 text-slate-900">
                        {formatCurrency(yearTotal)}
                      </td>
                    )
                  })}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Justification & Assumptions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4 bg-slate-50">
          <h4 className="font-semibold text-slate-800 mb-2">Justification</h4>
          <p className="text-sm text-slate-600">{localData?.justification}</p>
        </Card>

        <Card className="p-4 bg-slate-50">
          <h4 className="font-semibold text-slate-800 mb-2">Key Assumptions</h4>
          <ul className="text-sm text-slate-600 space-y-1">
            {localData?.assumptions?.map((assumption: string, index: number) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-green-600 mt-0.5">•</span>
                <span>{assumption}</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      {/* Chart Placeholder */}
      <div className="mt-8 p-8 bg-slate-50 rounded-lg border border-slate-200 text-center">
        <PieChart className="w-12 h-12 text-slate-400 mx-auto mb-3" />
        <p className="text-slate-600 font-medium">Cost Distribution Visualization</p>
        <p className="text-sm text-slate-500 mt-1">Interactive charts showing cost breakdown by category and year</p>
      </div>
    </Card>
  )
}
