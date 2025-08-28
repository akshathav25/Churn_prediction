'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { API_BASE_URL } from '@/lib/config'
import Toast from '@/components/Toast'
import Spinner from '@/components/Spinner'

interface SchemaField {
  name: string
  type: 'number' | 'categorical'
  values?: string[]
}

export default function PredictPage() {
  const [fields, setFields] = useState<SchemaField[] | null>(null)
  const [target, setTarget] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<{ prediction: number; probability: number } | null>(null)
  const [form, setForm] = useState<Record<string, any>>({})

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch(`${API_BASE_URL}/schema`)
        if (!res.ok) throw new Error(await res.text())
        const data = await res.json()
        setFields(data.fields)
        setTarget(data.target)
        const initial: Record<string, any> = {}
        data.fields.forEach((f: SchemaField) => {
          if (f.type === 'number') initial[f.name] = 0
          else if (f.type === 'categorical') initial[f.name] = (f.values && f.values[0]) || ''
        })
        setForm(initial)
      } catch (e: any) {
        setError(e?.message || 'Failed to load schema. Please train the model first.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const setField = (name: string, value: any) => {
    setForm(prev => ({ ...prev, [name]: value }))
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setResult(data)
    } catch (e: any) {
      setError(e?.message || 'Prediction failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="text-xl font-semibold">Single Prediction</div>
          <Link href="/" className="text-blue-600 hover:underline text-sm">Back to Dashboard</Link>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {loading && <div className="text-gray-600 flex items-center"><Spinner /><span className="ml-2">Loading schema...</span></div>}
        {fields && (
          <form onSubmit={onSubmit} className="bg-white border rounded p-6 shadow-sm space-y-4">
            {fields.map(f => (
              <div key={f.name} className="grid grid-cols-1 md:grid-cols-3 items-center gap-3">
                <label className="text-sm text-gray-700">{f.name}</label>
                <div className="md:col-span-2">
                  {f.type === 'number' ? (
                    <input
                      type="number"
                      className="border rounded px-3 py-2 w-full"
                      value={form[f.name] ?? 0}
                      onChange={(e) => setField(f.name, e.target.value === '' ? '' : Number(e.target.value))}
                    />
                  ) : (
                    <select
                      className="border rounded px-3 py-2 w-full"
                      value={form[f.name] ?? ''}
                      onChange={(e) => setField(f.name, e.target.value)}
                    >
                      {(f.values || []).map(v => (
                        <option key={v} value={v}>{v}</option>
                      ))}
                    </select>
                  )}
                </div>
              </div>
            ))}

            <div className="pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="bg-green-600 hover:bg-green-700 text-white rounded px-4 py-2 disabled:opacity-50 flex items-center"
              >
                {submitting ? (<><Spinner /><span className="ml-2">Predicting...</span></>) : 'Predict'}
              </button>
            </div>
          </form>
        )}

        {result && (
          <div className="bg-white border rounded p-6 shadow-sm mt-6">
            <div className="text-gray-800">Predicted label: <span className="font-semibold">{result.prediction}</span></div>
            <div className="text-gray-800">Probability: <span className="font-semibold">{(result.probability * 100).toFixed(2)}%</span></div>
          </div>
        )}
      </main>

      {error && <Toast message={error} onClose={() => setError(null)} />}
    </div>
  )
}
