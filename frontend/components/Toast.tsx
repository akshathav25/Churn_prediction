"use client"

import { useEffect } from 'react'

type ToastProps = {
  message: string
  onClose: () => void
  durationMs?: number
}

export default function Toast({ message, onClose, durationMs = 4000 }: ToastProps) {
  useEffect(() => {
    const id = setTimeout(onClose, durationMs)
    return () => clearTimeout(id)
  }, [onClose, durationMs])

  return (
    <div className="fixed top-4 right-4 z-50">
      <div className="bg-red-600 text-white px-4 py-3 rounded shadow-lg min-w-[240px] flex items-start">
        <span className="flex-1 text-sm">{message}</span>
        <button onClick={onClose} className="ml-3 text-white/90 hover:text-white">×</button>
      </div>
    </div>
  )
}
