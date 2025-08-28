'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import Link from 'next/link'
import { API_BASE_URL } from '@/lib/config'
import Toast from '@/components/Toast'
import Spinner from '@/components/Spinner'

interface Metrics {
  accuracy: number
  precision: number
  recall: number
  f1_score: number
  roc_auc: number
  confusion_matrix?: {
    true_negatives: number
    false_positives: number
    false_negatives: number
    true_positives: number
  }
}

export default function Dashboard() {
  const [target, setTarget] = useState<string>('')
  const [training, setTraining] = useState(false)
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [trainError, setTrainError] = useState<string | null>(null)

  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [batchError, setBatchError] = useState<string | null>(null)
  const [batchPreview, setBatchPreview] = useState<string[][] | null>(null)
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null)

  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    if (!metrics?.confusion_matrix || !canvasRef.current) return
    const cm = metrics.confusion_matrix
    const matrix = [
      [cm.true_negatives, cm.false_positives],
      [cm.false_negatives, cm.true_positives],
    ]
    // Flatten matrix for max calculation
    const flattened = matrix.reduce((acc, row) => acc.concat(row), [] as number[])
    const maxVal = Math.max(...flattened) || 1
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const width = canvas.width
    const height = canvas.height
    ctx.clearRect(0, 0, width, height)
    const cellW = width / 2
    const cellH = height / 2
    const labels = [
      ['TN', 'FP'],
      ['FN', 'TP']
    ]
    for (let r = 0; r < 2; r++) {
      for (let c = 0; c < 2; c++) {
        const val = matrix[r][c]
        const intensity = Math.floor(255 - (val / maxVal) * 180)
        ctx.fillStyle = `rgb(${intensity}, ${intensity}, 255)`
        ctx.fillRect(c * cellW, r * cellH, cellW, cellH)
        ctx.strokeStyle = '#333'
        ctx.strokeRect(c * cellW, r * cellH, cellW, cellH)
        ctx.fillStyle = '#111'
        ctx.font = 'bold 16px sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(`${labels[r][c]}: ${val}`, c * cellW + cellW / 2, r * cellH + cellH / 2)
      }
    }
  }, [metrics])

  const onTrain = async () => {
    setTraining(true)
    setTrainError(null)
    setMetrics(null)
    try {
      const url = target.trim() ? `${API_BASE_URL}/train?target=${encodeURIComponent(target.trim())}` : `${API_BASE_URL}/train`
      const res = await fetch(url, { method: 'POST' })
      if (!res.ok) {
        throw new Error(await res.text())
      }
      const data = await res.json()
      setMetrics(data.metrics)
    } catch (e: any) {
      setTrainError(e?.message || 'Training failed')
    } finally {
      setTraining(false)
    }
  }

  const parseCsv = (text: string): string[][] => {
    const lines = text.trim().split(/\r?\n/)
    return lines.map(line => line.split(','))
  }

  const onUpload = async () => {
    if (!file) return
    setUploading(true)
    setBatchError(null)
    setBatchPreview(null)
    setDownloadUrl(null)
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch(`${API_BASE_URL}/predict-batch`, { method: 'POST', body: form })
      if (!res.ok) throw new Error(await res.text())
      
      // Get the full CSV content for preview and download
      const csvText = await res.text()
      const rows = parseCsv(csvText)
      setBatchPreview(rows.slice(0, 15)) // Show first 15 rows
      
      // Create blob URL for download
      const blob = new Blob([csvText], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      setDownloadUrl(url)
    } catch (e: any) {
      setBatchError(e?.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const downloadCsv = () => {
    if (!downloadUrl) return
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = `predictions_${file?.name || 'data.csv'}`
    document.body.appendChild(a)
    a.click()
    a.remove()
  }

  // Cleanup blob URL on unmount
  useEffect(() => {
    return () => {
      if (downloadUrl) {
        URL.revokeObjectURL(downloadUrl)
      }
    }
  }, [downloadUrl])

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="text-xl font-semibold">Churn Analysis</div>
          <div className="text-sm text-gray-500">API: {API_BASE_URL}</div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Train Model */}
          <div className="bg-white border rounded-lg p-5 shadow-sm">
            <h2 className="text-lg font-semibold mb-3">Train Model</h2>
            <label className="block text-sm text-gray-600 mb-2">Target column (optional)</label>
            <input
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="e.g., Exited"
              className="w-full border rounded px-3 py-2 mb-3"
            />
            <button
              onClick={onTrain}
              disabled={training}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded px-4 py-2 disabled:opacity-50 flex items-center justify-center"
            >
              {training ? (<><Spinner /><span className="ml-2">Training...</span></>) : 'Train'}
            </button>
            {metrics && (
              <div className="mt-4 space-y-2 text-sm">
                <div>Accuracy: <span className="font-semibold">{metrics.accuracy.toFixed(4)}</span></div>
                <div>Precision: <span className="font-semibold">{metrics.precision.toFixed(4)}</span></div>
                <div>Recall: <span className="font-semibold">{metrics.recall.toFixed(4)}</span></div>
                <div>F1: <span className="font-semibold">{metrics.f1_score.toFixed(4)}</span></div>
                <div>ROC AUC: <span className="font-semibold">{metrics.roc_auc.toFixed(4)}</span></div>
                {metrics.confusion_matrix && (
                  <div className="mt-3">
                    <div className="text-gray-700 mb-2">Confusion Matrix</div>
                    <canvas ref={canvasRef} width={240} height={240} className="border rounded" />
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Upload Test CSV */}
          <div className="bg-white border rounded-lg p-5 shadow-sm">
            <h2 className="text-lg font-semibold mb-3">Upload Test CSV</h2>
            <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} className="mb-3" />
            <button
              onClick={onUpload}
              disabled={uploading || !file}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded px-4 py-2 disabled:opacity-50 flex items-center justify-center"
            >
              {uploading ? (<><Spinner /><span className="ml-2">Uploading...</span></>) : 'Predict Batch'}
            </button>
            {batchPreview && (
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm text-gray-700">Preview (first 15 rows)</div>
                  {downloadUrl && (
                    <button 
                      onClick={downloadCsv} 
                      className="text-blue-600 text-sm hover:underline font-medium"
                    >
                      Download Full CSV
                    </button>
                  )}
                </div>
                <div className="max-h-64 overflow-auto border rounded">
                  <table className="min-w-full text-xs">
                    <tbody>
                      {batchPreview.map((row, i) => (
                        <tr key={i} className={i === 0 ? 'bg-gray-100 font-semibold' : ''}>
                          {row.map((cell, j) => (
                            <td key={j} className="px-2 py-1 border">{cell}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {batchPreview.length === 15 && (
                  <div className="text-xs text-gray-500 mt-2 text-center">
                    Showing first 15 rows. Use "Download Full CSV" for complete results.
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Single Prediction */}
          <div className="bg-white border rounded-lg p-5 shadow-sm">
            <h2 className="text-lg font-semibold mb-3">Single Prediction</h2>
            <p className="text-sm text-gray-600 mb-4">Fill a form based on schema and get a prediction.</p>
            <Link href="/predict" className="inline-block w-full text-center bg-green-600 hover:bg-green-700 text-white rounded px-4 py-2">
              Go to Form
            </Link>
          </div>
        </div>
      </main>

      {trainError && <Toast message={trainError} onClose={() => setTrainError(null)} />}
      {batchError && <Toast message={batchError} onClose={() => setBatchError(null)} />}
    </div>
  )
}
