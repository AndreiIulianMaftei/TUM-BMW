"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { FileText, Edit3, Save, Loader2, TrendingUp, DollarSign } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Slider } from "@/components/ui/slider"

interface IncomeAnalysisSectionProps {
  pdfText: string
  marketData: any
  costData: any
  onDataChange: (data: any) => void
  incomeData: any
  selectedModel: "Royalties" | "Subscription" | "Single Buy" | null
  onModelChange: (model: "Royalties" | "Subscription" | "Single Buy") => void
}

export default function IncomeAnalysisSection({
  pdfText,
  marketData,
  costData,
  onDataChange,
  incomeData,
  selectedModel,
  onModelChange,
}: IncomeAnalysisSectionProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [isEditMode, setIsEditMode] = useState(false)
  const [localData, setLocalData] = useState<any>(incomeData)

  // Model-specific parameters
  const [royaltyRate, setRoyaltyRate] = useState(15)
  const [avgBundlePrice, setAvgBundlePrice] = useState(500)
  const [subscriptionPrice, setSubscriptionPrice] = useState(29.99)
  const [churnRate, setChurnRate] = useState(5)
  const [singleBuyPrice, setSingleBuyPrice] = useState(299)
  const [repeatPurchaseRate, setRepeatPurchaseRate] = useState(20)

  useEffect(() => {
    if (incomeData) {
      setLocalData(incomeData)
    }
  }, [incomeData])

  const generateAnalysis = async () => {
    setIsGenerating(true)

    await new Promise((resolve) => setTimeout(resolve, 2000))

    const years = Object.keys(marketData?.SOM?.numbers || {})
    const totalCosts = costData?.total_costs
      ? Object.values(costData.total_costs).reduce((sum: number, val: any) => sum + val, 0)
      : 0

    // Generate data for all three models
    const royaltiesModel: any = { yearly_revenue: {}, yearly_profit: {}, yearly_margin: {} }
    const subscriptionModel: any = { yearly_revenue: {}, yearly_profit: {}, yearly_margin: {} }
    const singleBuyModel: any = { yearly_revenue: {}, yearly_profit: {}, yearly_margin: {} }

    years.forEach((year, index) => {
      const som = marketData.SOM.numbers[year]
      const salesVolume = Math.round(som * 0.2) // 20% of SOM
      const yearCosts = totalCosts * (1 + index * 0.05)

      // Royalties Model
      const royaltyRevenue = salesVolume * avgBundlePrice * (royaltyRate / 100)
      royaltiesModel.yearly_revenue[year] = Math.round(royaltyRevenue)
      royaltiesModel.yearly_profit[year] = Math.round(royaltyRevenue - yearCosts)
      royaltiesModel.yearly_margin[year] = ((royaltyRevenue - yearCosts) / royaltyRevenue) * 100

      // Subscription Model
      const subscribers = salesVolume
      const monthlyRevenue = subscribers * subscriptionPrice * 12
      const adjustedRevenue = monthlyRevenue * (1 - churnRate / 100)
      subscriptionModel.yearly_revenue[year] = Math.round(adjustedRevenue)
      subscriptionModel.yearly_profit[year] = Math.round(adjustedRevenue - yearCosts)
      subscriptionModel.yearly_margin[year] = ((adjustedRevenue - yearCosts) / adjustedRevenue) * 100

      // Single Buy Model
      const singleBuyRevenue = salesVolume * singleBuyPrice
      const repeatRevenue = singleBuyRevenue * (repeatPurchaseRate / 100)
      const totalSingleRevenue = singleBuyRevenue + repeatRevenue
      singleBuyModel.yearly_revenue[year] = Math.round(totalSingleRevenue)
      singleBuyModel.yearly_profit[year] = Math.round(totalSingleRevenue - yearCosts)
      singleBuyModel.yearly_margin[year] = ((totalSingleRevenue - yearCosts) / totalSingleRevenue) * 100
    })

    const mockData = {
      models: {
        Royalties: {
          ...royaltiesModel,
          parameters: {
            royalty_rate: royaltyRate,
            avg_bundle_price: avgBundlePrice,
          },
          description: "Revenue based on percentage of each accessory bundle sale",
          pros: ["Low upfront investment", "Scales with BMW sales", "Aligned incentives with dealers"],
          cons: ["Dependent on BMW sales volume", "Lower margins", "Less predictable revenue"],
        },
        Subscription: {
          ...subscriptionModel,
          parameters: {
            monthly_price: subscriptionPrice,
            churn_rate: churnRate,
          },
          description: "Recurring monthly subscription for premium features and content",
          pros: ["Predictable recurring revenue", "High customer lifetime value", "Strong cash flow"],
          cons: ["Requires ongoing value delivery", "Churn management critical", "Higher marketing costs"],
        },
        "Single Buy": {
          ...singleBuyModel,
          parameters: {
            unit_price: singleBuyPrice,
            repeat_purchase_rate: repeatPurchaseRate,
          },
          description: "One-time purchase with potential for repeat sales",
          pros: ["Immediate revenue recognition", "Simple pricing model", "Lower customer acquisition cost"],
          cons: ["Revenue volatility", "Requires constant new customer acquisition", "Limited recurring revenue"],
        },
      },
      comparison: {
        best_revenue: "Subscription",
        best_profit: "Subscription",
        best_margin: "Royalties",
        recommendation:
          "Subscription model offers the best balance of revenue predictability and growth potential, though requires strong customer retention strategy.",
      },
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

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`
  }

  const getModelColor = (model: string) => {
    switch (model) {
      case "Royalties":
        return "blue"
      case "Subscription":
        return "purple"
      case "Single Buy":
        return "green"
      default:
        return "slate"
    }
  }

  const updateModelParameter = (model: string, param: string, value: number) => {
    const updated = { ...localData }
    updated.models[model].parameters[param] = value
    setLocalData(updated)
    onDataChange(updated)
  }

  if (!localData && !isGenerating) {
    return (
      <Card className="p-8 bg-white/80 backdrop-blur-sm border-purple-200 shadow-lg">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
            <FileText className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800">Income Analysis</h2>
            <p className="text-slate-600 text-sm">Generate revenue models and profit projections</p>
          </div>
        </div>

        <div className="text-center py-12">
          <p className="text-slate-600 mb-6">Generate income analysis with three revenue models</p>
          <Button onClick={generateAnalysis} size="lg" className="px-8 bg-purple-600 hover:bg-purple-700">
            <FileText className="w-5 h-5 mr-2" />
            Generate Income Analysis
          </Button>
        </div>
      </Card>
    )
  }

  if (isGenerating) {
    return (
      <Card className="p-8 bg-white/80 backdrop-blur-sm border-purple-200 shadow-lg">
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="w-16 h-16 text-purple-600 animate-spin mb-4" />
          <p className="text-lg font-medium text-slate-700">Generating income analysis with AI...</p>
          <p className="text-sm text-slate-500 mt-2">Calculating revenue models and profit projections</p>
        </div>
      </Card>
    )
  }

  const models = Object.keys(localData?.models || {})
  const years = Object.keys(localData?.models?.[models[0]]?.yearly_revenue || {})

  return (
    <Card className="p-8 bg-white/80 backdrop-blur-sm border-purple-200 shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
            <FileText className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800">Income Analysis</h2>
            <p className="text-slate-600 text-sm">Revenue Models & Profit Projections</p>
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

      {/* Model Selection */}
      <div className="mb-8">
        <Label className="text-sm font-medium mb-3 block">Select Revenue Model</Label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {models.map((model) => {
            const color = getModelColor(model)
            const isSelected = selectedModel === model
            return (
              <motion.button
                key={model}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onModelChange(model as any)}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  isSelected
                    ? `border-${color}-500 bg-${color}-50 shadow-lg`
                    : `border-slate-200 bg-white hover:border-${color}-300`
                }`}
              >
                <h3 className="font-semibold text-slate-800 mb-1">{model}</h3>
                <p className="text-xs text-slate-600">{localData.models[model].description}</p>
                {isSelected && (
                  <div className="mt-2 flex items-center gap-1 text-xs font-medium text-blue-600">
                    <TrendingUp className="w-3 h-3" />
                    Selected
                  </div>
                )}
              </motion.button>
            )
          })}
        </div>
      </div>

      {/* Model Parameters */}
      {isEditMode && (
        <div className="mb-8 p-6 bg-slate-50 rounded-lg border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Adjust Model Parameters</h3>
          <Tabs defaultValue="Royalties" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="Royalties">Royalties</TabsTrigger>
              <TabsTrigger value="Subscription">Subscription</TabsTrigger>
              <TabsTrigger value="Single Buy">Single Buy</TabsTrigger>
            </TabsList>

            <TabsContent value="Royalties" className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Royalty Rate (%)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    value={[royaltyRate]}
                    onValueChange={([value]) => {
                      setRoyaltyRate(value)
                      updateModelParameter("Royalties", "royalty_rate", value)
                    }}
                    min={5}
                    max={30}
                    step={1}
                    className="flex-1"
                  />
                  <span className="text-sm font-medium w-12 text-right">{royaltyRate}%</span>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Average Bundle Price ($)</Label>
                <Input
                  type="number"
                  value={avgBundlePrice}
                  onChange={(e) => {
                    setAvgBundlePrice(Number(e.target.value))
                    updateModelParameter("Royalties", "avg_bundle_price", Number(e.target.value))
                  }}
                />
              </div>
            </TabsContent>

            <TabsContent value="Subscription" className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Monthly Subscription Price ($)</Label>
                <Input
                  type="number"
                  value={subscriptionPrice}
                  onChange={(e) => {
                    setSubscriptionPrice(Number(e.target.value))
                    updateModelParameter("Subscription", "monthly_price", Number(e.target.value))
                  }}
                  step="0.01"
                />
              </div>
              <div className="space-y-2">
                <Label>Monthly Churn Rate (%)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    value={[churnRate]}
                    onValueChange={([value]) => {
                      setChurnRate(value)
                      updateModelParameter("Subscription", "churn_rate", value)
                    }}
                    min={0}
                    max={20}
                    step={0.5}
                    className="flex-1"
                  />
                  <span className="text-sm font-medium w-12 text-right">{churnRate}%</span>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="Single Buy" className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Unit Price ($)</Label>
                <Input
                  type="number"
                  value={singleBuyPrice}
                  onChange={(e) => {
                    setSingleBuyPrice(Number(e.target.value))
                    updateModelParameter("Single Buy", "unit_price", Number(e.target.value))
                  }}
                />
              </div>
              <div className="space-y-2">
                <Label>Repeat Purchase Rate (%)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    value={[repeatPurchaseRate]}
                    onValueChange={([value]) => {
                      setRepeatPurchaseRate(value)
                      updateModelParameter("Single Buy", "repeat_purchase_rate", value)
                    }}
                    min={0}
                    max={50}
                    step={5}
                    className="flex-1"
                  />
                  <span className="text-sm font-medium w-12 text-right">{repeatPurchaseRate}%</span>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      )}

      {/* Revenue Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {models.map((model) => {
          const color = getModelColor(model)
          const lastYear = years[years.length - 1]
          const revenue = localData.models[model].yearly_revenue[lastYear]
          const profit = localData.models[model].yearly_profit[lastYear]
          const margin = localData.models[model].yearly_margin[lastYear]

          return (
            <motion.div
              key={model}
              whileHover={{ scale: 1.02 }}
              className={`p-6 bg-gradient-to-br from-${color}-50 to-${color}-100 rounded-xl border-2 border-${color}-200`}
            >
              <h3 className="font-semibold text-slate-800 mb-4">{model}</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-slate-600 uppercase tracking-wide">Revenue ({lastYear})</p>
                  <p className="text-2xl font-bold text-slate-900">{formatCurrency(revenue)}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-600 uppercase tracking-wide">Profit ({lastYear})</p>
                  <p className={`text-xl font-bold ${profit > 0 ? "text-green-700" : "text-red-700"}`}>
                    {formatCurrency(profit)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-600 uppercase tracking-wide">Margin</p>
                  <p className="text-lg font-semibold text-slate-700">{formatPercentage(margin)}</p>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Yearly Breakdown Table */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">Yearly Financial Projections</h3>
        <Tabs defaultValue="revenue" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="revenue">Revenue</TabsTrigger>
            <TabsTrigger value="profit">Profit</TabsTrigger>
            <TabsTrigger value="margin">Margin</TabsTrigger>
          </TabsList>

          {["revenue", "profit", "margin"].map((metric) => (
            <TabsContent key={metric} value={metric}>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left py-3 px-4 font-semibold text-slate-700">Model</th>
                      {years.map((year) => (
                        <th key={year} className="text-right py-3 px-4 font-semibold text-slate-700">
                          {year}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {models.map((model) => (
                      <tr key={model} className="border-b border-slate-100 hover:bg-slate-50">
                        <td className="py-3 px-4 font-medium text-slate-700">{model}</td>
                        {years.map((year) => {
                          const value = localData.models[model][`yearly_${metric}`][year]
                          return (
                            <td key={year} className="text-right py-3 px-4 text-slate-600">
                              {metric === "margin" ? formatPercentage(value) : formatCurrency(value)}
                            </td>
                          )
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </div>

      {/* Pros & Cons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {models.map((model) => (
          <Card key={model} className="p-4 bg-slate-50">
            <h4 className="font-semibold text-slate-800 mb-3">{model}</h4>
            <div className="space-y-3">
              <div>
                <p className="text-xs font-semibold text-green-600 uppercase mb-1">Pros</p>
                <ul className="text-xs text-slate-600 space-y-1">
                  {localData.models[model].pros.map((pro: string, index: number) => (
                    <li key={index} className="flex items-start gap-1">
                      <span className="text-green-600">+</span>
                      <span>{pro}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold text-red-600 uppercase mb-1">Cons</p>
                <ul className="text-xs text-slate-600 space-y-1">
                  {localData.models[model].cons.map((con: string, index: number) => (
                    <li key={index} className="flex items-start gap-1">
                      <span className="text-red-600">-</span>
                      <span>{con}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Recommendation */}
      <Card className="p-6 bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-200">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
            <DollarSign className="w-5 h-5 text-white" />
          </div>
          <div>
            <h4 className="font-semibold text-slate-800 mb-2">AI Recommendation</h4>
            <p className="text-sm text-slate-700">{localData.comparison?.recommendation}</p>
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                Best Revenue: {localData.comparison?.best_revenue}
              </span>
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded">
                Best Profit: {localData.comparison?.best_profit}
              </span>
              <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded">
                Best Margin: {localData.comparison?.best_margin}
              </span>
            </div>
          </div>
        </div>
      </Card>
    </Card>
  )
}
