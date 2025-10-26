"use client"

import { useState, useCallback } from "react"
import { motion } from "framer-motion"
import { Upload, FileText, CheckCircle, Loader2 } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useDropzone } from "react-dropzone"

interface PdfUploadSectionProps {
  onUpload: (text: string, fileName: string) => void
  fileName?: string
}

export default function PdfUploadSection({ onUpload, fileName }: PdfUploadSectionProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<string | null>(fileName || null)
  const [fileSize, setFileSize] = useState<number>(0)

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0]
      if (!file) return

      setIsUploading(true)
      setFileSize(file.size)

      try {
        // In a real app, you would extract PDF text here
        // For now, we'll simulate it
        await new Promise((resolve) => setTimeout(resolve, 1500))

        const mockText = `BMW Motorrad Accessory Bundles Analysis Document
        
This document contains market analysis for BMW Motorrad accessory bundles...
[Simulated PDF content - In production, this would be actual extracted text]`

        setUploadedFile(file.name)
        onUpload(mockText, file.name)
      } catch (error) {
        console.error("Error uploading PDF:", error)
      } finally {
        setIsUploading(false)
      }
    },
    [onUpload],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
  })

  return (
    <Card className="p-8 bg-white/80 backdrop-blur-sm border-blue-200 shadow-lg">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
          <Upload className="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Upload Document</h2>
          <p className="text-slate-600 text-sm">Upload your PDF for AI-powered analysis</p>
        </div>
      </div>

      {!uploadedFile ? (
        <motion.div
          {...getRootProps()}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
            isDragActive ? "border-blue-500 bg-blue-50" : "border-slate-300 hover:border-blue-400 hover:bg-slate-50"
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center gap-4">
            {isUploading ? (
              <>
                <Loader2 className="w-16 h-16 text-blue-600 animate-spin" />
                <p className="text-lg font-medium text-slate-700">Extracting text from PDF...</p>
              </>
            ) : (
              <>
                <FileText className="w-16 h-16 text-slate-400" />
                <div>
                  <p className="text-lg font-medium text-slate-700">
                    {isDragActive ? "Drop your PDF here" : "Drag & drop your PDF here"}
                  </p>
                  <p className="text-sm text-slate-500 mt-1">or click to browse files</p>
                </div>
                <Button type="button" variant="outline" className="mt-2 bg-transparent">
                  Choose File
                </Button>
              </>
            )}
          </div>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-green-50 border-2 border-green-200 rounded-xl p-6"
        >
          <div className="flex items-center gap-4">
            <CheckCircle className="w-12 h-12 text-green-600 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-semibold text-green-900">File uploaded successfully!</p>
              <p className="text-sm text-green-700 mt-1">{uploadedFile}</p>
              <p className="text-xs text-green-600 mt-1">Size: {(fileSize / 1024).toFixed(2)} KB</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setUploadedFile(null)
                setFileSize(0)
              }}
            >
              Upload Different File
            </Button>
          </div>
        </motion.div>
      )}

      {uploadedFile && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">
            <strong>✓ Ready for analysis</strong> - Scroll down to generate market analysis, cost breakdown, and income
            projections.
          </p>
        </div>
      )}
    </Card>
  )
}
