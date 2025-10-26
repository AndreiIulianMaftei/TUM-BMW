"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { MessageSquare, Send, Loader2, Bot, User, Sparkles } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface ChatbotSectionProps {
  marketData: any
  costData: any
  incomeData: any
  onMarketDataChange: (data: any) => void
  onCostDataChange: (data: any) => void
  onIncomeDataChange: (data: any) => void
}

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export default function ChatbotSection({
  marketData,
  costData,
  incomeData,
  onMarketDataChange,
  onCostDataChange,
  onIncomeDataChange,
}: ChatbotSectionProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello! I'm your AI assistant for market analysis. I can help you modify your TAM/SAM/SOM values, adjust cost projections, update income models, or answer questions about your analysis. What would you like to do?",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate AI response - in production, this would call your OpenAI endpoint
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // Parse user intent and generate appropriate response
    const lowerInput = input.toLowerCase()
    let responseContent = ""
    let dataUpdated = false

    if (lowerInput.includes("tam") || lowerInput.includes("market")) {
      responseContent =
        "I can help you adjust your Total Addressable Market (TAM) values. For example, you could say:\n\n• 'Increase TAM by 10%'\n• 'Set TAM for 2025 to 6 million'\n• 'Show me current TAM values'\n\nWhat would you like to do with your market data?"
    } else if (lowerInput.includes("cost") || lowerInput.includes("expense")) {
      responseContent =
        "I can help you modify your cost structure. You could say:\n\n• 'Reduce marketing costs by 15%'\n• 'Add a new cost item for R&D'\n• 'Show me the cost breakdown'\n\nWhat cost adjustments would you like to make?"
    } else if (lowerInput.includes("income") || lowerInput.includes("revenue") || lowerInput.includes("profit")) {
      responseContent =
        "I can help you adjust your income models. You could say:\n\n• 'Increase subscription price to $39.99'\n• 'Change royalty rate to 20%'\n• 'Compare all three models'\n\nWhat income parameters would you like to modify?"
    } else if (lowerInput.includes("increase") && lowerInput.includes("%")) {
      // Example: "increase TAM by 10%"
      const percentMatch = lowerInput.match(/(\d+)%/)
      if (percentMatch && marketData) {
        const percent = Number.parseInt(percentMatch[1])
        const updatedMarketData = { ...marketData }
        Object.keys(updatedMarketData.TAM.numbers).forEach((year) => {
          updatedMarketData.TAM.numbers[year] = Math.round(updatedMarketData.TAM.numbers[year] * (1 + percent / 100))
        })
        onMarketDataChange(updatedMarketData)
        responseContent = `I've increased your TAM values by ${percent}%. The changes have been applied across all years. Your new TAM projections are now higher, which will also affect your SAM and SOM calculations.`
        dataUpdated = true
      }
    } else if (lowerInput.includes("summary") || lowerInput.includes("overview")) {
      const lastYear = marketData ? Object.keys(marketData.TAM.numbers).pop() : "N/A"
      const tam = marketData?.TAM?.numbers?.[lastYear] || 0
      const totalCost = costData?.total_costs
        ? Object.values(costData.total_costs).reduce((sum: number, val: any) => sum + val, 0)
        : 0

      responseContent = `Here's a summary of your analysis:\n\n**Market Size (${lastYear}):**\n• TAM: ${(tam / 1000000).toFixed(1)}M\n\n**Total Costs:**\n• ${(totalCost / 1000000).toFixed(1)}M annually\n\n**Income Models:**\n• 3 models analyzed (Royalties, Subscription, Single Buy)\n\nWould you like me to dive deeper into any specific area?`
    } else {
      responseContent =
        "I understand you want to make changes to your analysis. I can help you with:\n\n• **Market Analysis**: Adjust TAM, SAM, SOM values\n• **Cost Structure**: Modify cost categories and items\n• **Income Models**: Update pricing and revenue parameters\n• **General Questions**: Get insights about your data\n\nPlease be more specific about what you'd like to change, and I'll help you make those adjustments!"
    }

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: responseContent,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, assistantMessage])
    setIsLoading(false)

    if (dataUpdated) {
      // Show a success indicator
      setTimeout(() => {
        const updateMessage: Message = {
          id: (Date.now() + 2).toString(),
          role: "assistant",
          content: "✓ Data updated successfully! Scroll up to see the changes reflected in your analysis.",
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, updateMessage])
      }, 500)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const suggestedPrompts = [
    "Show me a summary of my analysis",
    "Increase TAM by 15%",
    "Reduce marketing costs by 20%",
    "Change subscription price to $34.99",
  ]

  return (
    <Card className="p-6 bg-white/80 backdrop-blur-sm border-indigo-200 shadow-lg">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center">
          <MessageSquare className="w-6 h-6 text-indigo-600" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-slate-800">AI Assistant</h2>
          <p className="text-slate-600 text-sm">Chat to modify your analysis with natural language</p>
        </div>
      </div>

      {/* Suggested Prompts */}
      {messages.length <= 1 && (
        <div className="mb-4">
          <p className="text-xs font-medium text-slate-600 mb-2">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedPrompts.map((prompt, index) => (
              <button
                key={index}
                onClick={() => setInput(prompt)}
                className="px-3 py-1.5 text-xs bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-full border border-indigo-200 transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages Container */}
      <div className="h-96 overflow-y-auto mb-4 space-y-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : "flex-row"}`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.role === "user" ? "bg-blue-600" : "bg-indigo-600"
                }`}
              >
                {message.role === "user" ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Bot className="w-4 h-4 text-white" />
                )}
              </div>
              <div className={`flex-1 max-w-[80%] ${message.role === "user" ? "text-right" : "text-left"}`}>
                <div
                  className={`inline-block p-3 rounded-lg ${
                    message.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-white text-slate-800 border border-slate-200"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1">
              <div className="inline-block p-3 rounded-lg bg-white border border-slate-200">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-indigo-600 animate-spin" />
                  <span className="text-sm text-slate-600">Thinking...</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me to modify your analysis... (Press Enter to send)"
            className="resize-none pr-10"
            rows={2}
            disabled={isLoading}
          />
          {input.trim() && <Sparkles className="absolute right-3 top-3 w-4 h-4 text-indigo-400" />}
        </div>
        <Button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className="px-6 bg-indigo-600 hover:bg-indigo-700"
          size="lg"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
        </Button>
      </div>

      {/* Info Banner */}
      <div className="mt-4 p-3 bg-indigo-50 rounded-lg border border-indigo-200">
        <p className="text-xs text-indigo-700">
          <strong>Tip:</strong> You can ask me to increase/decrease values, add new items, or explain any part of your
          analysis. I'll update your data in real-time!
        </p>
      </div>
    </Card>
  )
}
