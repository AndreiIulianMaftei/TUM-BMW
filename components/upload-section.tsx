"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { motion } from "framer-motion"
import { Upload, FileText, CheckCircle2, Loader2, TrendingUp, BarChart3, DollarSign } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"

interface UploadSectionProps {
  onUpload: (text: string) => void
}

export default function UploadSection({ onUpload }: UploadSectionProps) {
  const [file, setFile] = useState<File | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const { toast } = useToast()

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)

      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile && droppedFile.type === "application/pdf") {
        setFile(droppedFile)
      } else {
        toast({
          title: "Invalid file type",
          description: "Please upload a PDF file",
          variant: "destructive",
        })
      }
    },
    [toast],
  )

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const handleExtract = async () => {
    if (!file) return

    setIsProcessing(true)

    // Simulate PDF extraction (in real app, you'd use a PDF library)
    setTimeout(() => {
      const mockText = "BMW Motorrad Accessory Bundles Market Analysis..."
      onUpload(mockText)
      setIsProcessing(false)
      toast({
        title: "Success!",
        description: "PDF text extracted successfully",
      })
    }, 2000)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="border-2 border-dashed border-blue-200 bg-white/80 backdrop-blur-sm shadow-xl">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl">Upload Your Document</CardTitle>
            <CardDescription className="text-lg">Upload a PDF to begin your market analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div
              onDrop={handleDrop}
              onDragOver={(e) => {
                e.preventDefault()
                setIsDragging(true)
              }}
              onDragLeave={() => setIsDragging(false)}
              className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
                isDragging
                  ? "border-blue-500 bg-blue-50"
                  : "border-slate-300 bg-slate-50 hover:border-blue-400 hover:bg-blue-50/50"
              }`}
            >
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />

              <motion.div animate={{ y: isDragging ? -10 : 0 }} className="flex flex-col items-center gap-4">
                {file ? (
                  <>
                    <CheckCircle2 className="w-16 h-16 text-green-500" />
                    <div>
                      <p className="text-lg font-semibold text-slate-700">{file.name}</p>
                      <p className="text-sm text-slate-500 mt-1">{(file.size / 1024).toFixed(2)} KB</p>
                    </div>
                  </>
                ) : (
                  <>
                    <Upload className="w-16 h-16 text-blue-500" />
                    <div>
                      <p className="text-lg font-semibold text-slate-700">Drop your PDF here or click to browse</p>
                      <p className="text-sm text-slate-500 mt-2">Supports PDF files up to 10MB</p>
                    </div>
                  </>
                )}
              </motion.div>
            </div>

            {file && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6 flex justify-center"
              >
                <Button
                  onClick={handleExtract}
                  disabled={isProcessing}
                  size="lg"
                  className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-lg"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Extracting Text...
                    </>
                  ) : (
                    <>
                      <FileText className="w-5 h-5 mr-2" />
                      Extract & Continue
                    </>
                  )}
                </Button>
              </motion.div>
            )}
          </CardContent>
        </Card>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          {[
            {
              icon: TrendingUp,
              title: "Market Analysis",
              description: "TAM/SAM/SOM projections with AI insights",
            },
            {
              icon: BarChart3,
              title: "Cost Breakdown",
              description: "Comprehensive cost structure analysis",
            },
            {
              icon: DollarSign,
              title: "Revenue Models",
              description: "Multiple income strategy simulations",
            },
          ].map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
              >
                <Card className="bg-white/80 backdrop-blur-sm hover:shadow-lg transition-shadow">
                  <CardContent className="pt-6">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                      <Icon className="w-6 h-6 text-blue-600" />
                    </div>
                    <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                    <p className="text-sm text-slate-600">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}
        </div>
      </motion.div>
    </div>
  )
}
