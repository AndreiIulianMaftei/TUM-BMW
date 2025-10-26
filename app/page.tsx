"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Upload, Sparkles, FileText, TrendingUp, DollarSign, MessageSquare, Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import PdfUploadSection from "@/components/pdf-upload-section"
import MarketAnalysisSection from "@/components/market-analysis-section"
import CostAnalysisSection from "@/components/cost-analysis-section"
import IncomeAnalysisSection from "@/components/income-analysis-section"
import ChatbotSection from "@/components/chatbot-section"

export default function Home() {
  const [pdfText, setPdfText] = useState<string>("")
  const [pdfFileName, setPdfFileName] = useState<string>("")
  const [marketData, setMarketData] = useState<any>(null)
  const [costData, setCostData] = useState<any>(null)
  const [incomeData, setIncomeData] = useState<any>(null)
  const [selectedIncomeModel, setSelectedIncomeModel] = useState<"Royalties" | "Subscription" | "Single Buy" | null>(
    null,
  )

  const handlePdfUpload = (text: string, fileName: string) => {
    setPdfText(text)
    setPdfFileName(fileName)
  }

  const handleMarketDataChange = (data: any) => {
    setMarketData(data)
  }

  const handleCostDataChange = (data: any) => {
    setCostData(data)
  }

  const handleIncomeDataChange = (data: any) => {
    setIncomeData(data)
  }

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Fixed Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="sticky top-0 z-50 bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 text-white shadow-xl backdrop-blur-sm"
      >
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
                className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center"
              >
                <Sparkles className="w-6 h-6" />
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight">BMW MOTORRAD</h1>
                <p className="text-blue-100 text-sm">Market Analysis Dashboard</p>
              </div>
            </div>

            {/* Quick Navigation */}
            <nav className="hidden md:flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => scrollToSection("upload")}
                className="text-white hover:bg-white/10"
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => scrollToSection("market")}
                className="text-white hover:bg-white/10"
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                Market
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => scrollToSection("cost")}
                className="text-white hover:bg-white/10"
              >
                <DollarSign className="w-4 h-4 mr-2" />
                Cost
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => scrollToSection("income")}
                className="text-white hover:bg-white/10"
              >
                <FileText className="w-4 h-4 mr-2" />
                Income
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => scrollToSection("chat")}
                className="text-white hover:bg-white/10"
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                AI Chat
              </Button>
            </nav>
          </div>
        </div>
      </motion.header>

      {/* Main Content - Single Scrollable Page */}
      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* PDF Upload Section */}
        <motion.section
          id="upload"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <PdfUploadSection onUpload={handlePdfUpload} fileName={pdfFileName} />
        </motion.section>

        {/* Market Analysis Section */}
        {pdfText && (
          <motion.section
            id="market"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <MarketAnalysisSection pdfText={pdfText} onDataChange={handleMarketDataChange} marketData={marketData} />
          </motion.section>
        )}

        {/* Cost Analysis Section */}
        {marketData && (
          <motion.section
            id="cost"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <CostAnalysisSection
              pdfText={pdfText}
              marketData={marketData}
              onDataChange={handleCostDataChange}
              costData={costData}
            />
          </motion.section>
        )}

        {/* Income Analysis Section */}
        {costData && (
          <motion.section
            id="income"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <IncomeAnalysisSection
              pdfText={pdfText}
              marketData={marketData}
              costData={costData}
              onDataChange={handleIncomeDataChange}
              incomeData={incomeData}
              selectedModel={selectedIncomeModel}
              onModelChange={setSelectedIncomeModel}
            />
          </motion.section>
        )}

        {/* AI Chatbot Section */}
        {(marketData || costData || incomeData) && (
          <motion.section
            id="chat"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <ChatbotSection
              marketData={marketData}
              costData={costData}
              incomeData={incomeData}
              onMarketDataChange={setMarketData}
              onCostDataChange={setCostData}
              onIncomeDataChange={setIncomeData}
            />
          </motion.section>
        )}

        {/* Export Section */}
        {(marketData || costData || incomeData) && (
          <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Card className="p-6 bg-white/80 backdrop-blur-sm border-blue-200">
              <h2 className="text-2xl font-bold text-slate-800 mb-4 flex items-center gap-2">
                <Download className="w-6 h-6 text-blue-600" />
                Export Data
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {marketData && (
                  <Button
                    onClick={() => {
                      const blob = new Blob([JSON.stringify(marketData, null, 2)], { type: "application/json" })
                      const url = URL.createObjectURL(blob)
                      const a = document.createElement("a")
                      a.href = url
                      a.download = `market_analysis_${new Date().toISOString().split("T")[0]}.json`
                      a.click()
                    }}
                    className="w-full"
                  >
                    Download Market Data
                  </Button>
                )}
                {costData && (
                  <Button
                    onClick={() => {
                      const blob = new Blob([JSON.stringify(costData, null, 2)], { type: "application/json" })
                      const url = URL.createObjectURL(blob)
                      const a = document.createElement("a")
                      a.href = url
                      a.download = `cost_analysis_${new Date().toISOString().split("T")[0]}.json`
                      a.click()
                    }}
                    className="w-full"
                  >
                    Download Cost Data
                  </Button>
                )}
                {incomeData && (
                  <Button
                    onClick={() => {
                      const blob = new Blob([JSON.stringify(incomeData, null, 2)], { type: "application/json" })
                      const url = URL.createObjectURL(blob)
                      const a = document.createElement("a")
                      a.href = url
                      a.download = `income_analysis_${new Date().toISOString().split("T")[0]}.json`
                      a.click()
                    }}
                    className="w-full"
                  >
                    Download Income Data
                  </Button>
                )}
              </div>
            </Card>
          </motion.section>
        )}
      </div>

      {/* Footer */}
      <footer className="mt-20 border-t border-slate-200 bg-white/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-8 text-center text-slate-600">
          <p className="font-semibold">BMW MOTORRAD • Market Intelligence Dashboard</p>
          <p className="text-sm mt-2">Powered by AI-Driven Market Analysis | © 2025-2025</p>
          <p className="text-xs mt-1 text-slate-400">Confidential & Proprietary Information</p>
        </div>
      </footer>
    </div>
  )
}
