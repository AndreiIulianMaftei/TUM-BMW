"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { TrendingUp, Edit3, Save, Loader2, BarChart3 } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"

interface MarketAnalysisSectionProps {
  pdfText: string
  onDataChange: (data: any) => void
  marketData: any
}

export default function MarketAnalysisSection({ pdfText, onDataChange, marketData }: MarketAnalysisSectionProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [isEditMode, setIsEditMode] = useState(false)
  const [usePercentages, setUsePercentages] = useState(false)
  const [endYear, setEndYear] = useState(2030)
  const [samPercentage, setSamPercentage] = useState(50)
  const [somPercentage, setSomPercentage] = useState(30)
  const [volumePercentage, setVolumePercentage] = useState(20)

  const [localData, setLocalData] = useState<any>(marketData)

  useEffect(() => {
    if (marketData) {
      setLocalData(marketData)
    }
  }, [marketData])

  const generateAnalysis = async () => {
    setIsGenerating(true)

    // Simulate API call - in production, this would call your OpenAI endpoint
    await new Promise((resolve) => setTimeout(resolve, 2000))

    const mockData = {
      TAM: {
        description_of_public: "All BMW Motorrad owners and potential motorcycle enthusiasts in target markets",
        numbers: {
          "2024": 5000000,
          "2025": 5250000,
          "2026": 5512500,
          "2027": 5788125,
          "2028": 6077531,
          "2029": 6381408,
          "2030": 6700478,
        },
        justification:
          "Based on global motorcycle market size and BMW's market share, considering growth in premium motorcycle segment",
        industry_example: {
          name: "Harley-Davidson Accessories",
          description: "Similar premium motorcycle accessory market with comparable customer base",
          link: "https://example.com/harley-davidson",
        },
      },
      SAM: {
        description_of_public:
          "BMW Motorrad owners in regions with established dealer networks and digital infrastructure",
        numbers: {
          "2024": 2500000,
          "2025": 2625000,
          "2026": 2756250,
          "2027": 2894063,
          "2028": 3038766,
          "2029": 3190704,
          "2030": 3350239,
        },
        justification: "Approximately 50% of TAM can be effectively reached through existing distribution channels",
        industry_example: {
          name: "Ducati Performance Parts",
          description: "Premium motorcycle parts distribution through dealer network",
          link: "https://example.com/ducati",
        },
      },
      SOM: {
        description_of_public: "Active BMW Motorrad customers likely to purchase accessory bundles in near term",
        numbers: {
          "2024": 750000,
          "2025": 787500,
          "2026": 826875,
          "2027": 868219,
          "2028": 911630,
          "2029": 957211,
          "2030": 1005072,
        },
        justification: "Conservative 30% of SAM represents realistic market capture based on purchase intent data",
        industry_example: {
          name: "BMW Motorrad Connected",
          description: "Successful digital accessory platform with proven adoption rates",
          link: "https://example.com/bmw-connected",
        },
      },
      sources: [
        "https://example.com/motorcycle-market-report",
        "https://example.com/bmw-annual-report",
        "https://example.com/premium-accessories-study",
      ],
    }

    setLocalData(mockData)
    onDataChange(mockData)
    setIsGenerating(false)
  }

  const years = Array.from({ length: endYear - 2023 }, (_, i) => 2024 + i)

  const calculateSalesVolume = (year: number) => {
    if (!localData?.SOM?.numbers) return 0
    const som = localData.SOM.numbers[year.toString()] || 0
    return Math.round(som * (volumePercentage / 100))
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(0)}K`
    return num.toLocaleString()
  }

  const updateMarketValue = (market: "TAM" | "SAM" | "SOM", year: string, value: number) => {
    const updated = { ...localData }
    updated[market].numbers[year] = value
    setLocalData(updated)
    onDataChange(updated)
  }

  if (!localData && !isGenerating) {
    return (
      <Card className="p-8 bg-white/80 backdrop-blur-sm border-blue-200 shadow-lg">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <TrendingUp className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800">Market Analysis</h2>
            <p className="text-slate-600 text-sm">Generate TAM/SAM/SOM analysis with AI</p>
          </div>
        </div>

        <div className="text-center py-12">
          <p className="text-slate-600 mb-6">Generate comprehensive market analysis based on your uploaded document</p>
          <Button onClick={generateAnalysis} size="lg" className="px-8">
            <TrendingUp className="w-5 h-5 mr-2" />
            Generate Market Analysis
          </Button>
        </div>
      </Card>
    )
  }

  if (isGenerating) {
    return (
      <Card className="p-8 bg-white/80 backdrop-blur-sm border-blue-200 shadow-lg">
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="w-16 h-16 text-blue-600 animate-spin mb-4" />
          <p className="text-lg font-medium text-slate-700">Generating market analysis with AI...</p>
          <p className="text-sm text-slate-500 mt-2">Analyzing TAM, SAM, and SOM projections</p>
        </div>
      </Card>
    )
  }

  const firstYear = years[0]
  const lastYear = years[years.length - 1]

  const tamGrowth = localData?.TAM?.numbers
    ? ((localData.TAM.numbers[lastYear] - localData.TAM.numbers[firstYear]) / localData.TAM.numbers[firstYear]) * 100
    : 0
  const samGrowth = localData?.SAM?.numbers
    ? ((localData.SAM.numbers[lastYear] - localData.SAM.numbers[firstYear]) / localData.SAM.numbers[firstYear]) * 100
    : 0
  const somGrowth = localData?.SOM?.numbers
    ? ((localData.SOM.numbers[lastYear] - localData.SOM.numbers[firstYear]) / localData.SOM.numbers[firstYear]) * 100
    : 0

  return (
    <Card className="p-8 bg-white/80 backdrop-blur-sm border-blue-200 shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <TrendingUp className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800">Market Analysis</h2>
            <p className="text-slate-600 text-sm">TAM / SAM / SOM Projections</p>
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

      {/* Control Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="space-y-2">
          <Label className="text-sm font-medium">Analysis Period</Label>
          <select
            value={endYear}
            onChange={(e) => setEndYear(Number(e.target.value))}
            className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
          >
            {[2025, 2026, 2027, 2028, 2029, 2030].map((year) => (
              <option key={year} value={year}>
                {2024} - {year}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-sm font-medium">Percentage Mode</Label>
            <Switch checked={usePercentages} onCheckedChange={setUsePercentages} />
          </div>
          <p className="text-xs text-slate-600">Auto-calculate SAM/SOM from TAM</p>
        </div>

        <div className="space-y-2">
          <Label className="text-sm font-medium">Sales Volume</Label>
          <div className="flex items-center gap-2">
            <Slider
              value={[volumePercentage]}
              onValueChange={([value]) => setVolumePercentage(value)}
              min={0}
              max={100}
              step={5}
              className="flex-1"
            />
            <span className="text-sm font-medium w-12 text-right">{volumePercentage}%</span>
          </div>
          <p className="text-xs text-slate-600">% of SOM</p>
        </div>
      </div>

      {usePercentages && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
          <div className="space-y-2">
            <Label className="text-sm font-medium">SAM (% of TAM)</Label>
            <div className="flex items-center gap-2">
              <Slider
                value={[samPercentage]}
                onValueChange={([value]) => setSamPercentage(value)}
                min={0}
                max={100}
                step={1}
              />
              <span className="text-sm font-medium w-12 text-right">{samPercentage}%</span>
            </div>
          </div>
          <div className="space-y-2">
            <Label className="text-sm font-medium">SOM (% of SAM)</Label>
            <div className="flex items-center gap-2">
              <Slider
                value={[somPercentage]}
                onValueChange={([value]) => setSomPercentage(value)}
                min={0}
                max={100}
                step={1}
              />
              <span className="text-sm font-medium w-12 text-right">{somPercentage}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200"
        >
          <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-1">Total Addressable Market</p>
          <p className="text-2xl font-bold text-blue-900">{formatNumber(localData?.TAM?.numbers?.[lastYear] || 0)}</p>
          <p className="text-xs text-blue-700 mt-1">
            +{tamGrowth.toFixed(1)}% from {firstYear}
          </p>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200"
        >
          <p className="text-xs font-semibold text-green-600 uppercase tracking-wide mb-1">
            Serviceable Available Market
          </p>
          <p className="text-2xl font-bold text-green-900">{formatNumber(localData?.SAM?.numbers?.[lastYear] || 0)}</p>
          <p className="text-xs text-green-700 mt-1">
            +{samGrowth.toFixed(1)}% from {firstYear}
          </p>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-4 bg-gradient-to-br from-amber-50 to-amber-100 rounded-lg border border-amber-200"
        >
          <p className="text-xs font-semibold text-amber-600 uppercase tracking-wide mb-1">
            Serviceable Obtainable Market
          </p>
          <p className="text-2xl font-bold text-amber-900">{formatNumber(localData?.SOM?.numbers?.[lastYear] || 0)}</p>
          <p className="text-xs text-amber-700 mt-1">
            +{somGrowth.toFixed(1)}% from {firstYear}
          </p>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border border-purple-200"
        >
          <p className="text-xs font-semibold text-purple-600 uppercase tracking-wide mb-1">Projected Sales Volume</p>
          <p className="text-2xl font-bold text-purple-900">{formatNumber(calculateSalesVolume(lastYear))}</p>
          <p className="text-xs text-purple-700 mt-1">{volumePercentage}% of SOM</p>
        </motion.div>
      </div>

      {/* Editable Data Tables */}
      {isEditMode && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Edit Market Values</h3>
          <Tabs defaultValue="TAM" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="TAM">TAM</TabsTrigger>
              <TabsTrigger value="SAM">SAM</TabsTrigger>
              <TabsTrigger value="SOM">SOM</TabsTrigger>
            </TabsList>

            {["TAM", "SAM", "SOM"].map((market) => (
              <TabsContent key={market} value={market} className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {years.map((year) => (
                    <div key={year} className="space-y-2">
                      <Label className="text-sm">{year}</Label>
                      <Input
                        type="number"
                        value={localData?.[market]?.numbers?.[year] || 0}
                        onChange={(e) => updateMarketValue(market as any, year.toString(), Number(e.target.value))}
                        className="text-sm"
                      />
                    </div>
                  ))}
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      )}

      {/* Market Descriptions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {["TAM", "SAM", "SOM"].map((market) => (
          <Card key={market} className="p-4 bg-slate-50">
            <h4 className="font-semibold text-slate-800 mb-2">{market}</h4>
            <p className="text-sm text-slate-600 mb-3">{localData?.[market]?.description_of_public}</p>
            <details className="text-xs text-slate-500">
              <summary className="cursor-pointer font-medium mb-2">Justification</summary>
              <p>{localData?.[market]?.justification}</p>
            </details>
          </Card>
        ))}
      </div>

      {/* Simple Chart Placeholder */}
      <div className="p-8 bg-slate-50 rounded-lg border border-slate-200 text-center">
        <BarChart3 className="w-12 h-12 text-slate-400 mx-auto mb-3" />
        <p className="text-slate-600 font-medium">Market Growth Visualization</p>
        <p className="text-sm text-slate-500 mt-1">Interactive charts showing TAM/SAM/SOM trends over time</p>
      </div>
    </Card>
  )
}
