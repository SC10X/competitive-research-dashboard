import { useEffect, useState, useCallback } from 'react'
import { Toast } from '@/components/ui/Toast'

interface ApiErrorDetail {
  message: string
  status?: number
  url?: string
}

export default function GlobalErrorListener() {
  const [errors, setErrors] = useState<Array<{ id: number; detail: ApiErrorDetail }>>([])
  let nextId = 0

  const handleApiError = useCallback((e: Event) => {
    const detail = (e as CustomEvent).detail as ApiErrorDetail
    const id = Date.now()
    setErrors((prev) => [...prev.slice(-2), { id, detail }]) // keep last 3
  }, [])

  useEffect(() => {
    window.addEventListener('api-error', handleApiError)
    return () => window.removeEventListener('api-error', handleApiError)
  }, [handleApiError])

  const removeError = (id: number) => {
    setErrors((prev) => prev.filter((e) => e.id !== id))
  }

  return (
    <>
      {errors.map(({ id, detail }) => (
        <Toast
          key={id}
          type="error"
          message={detail.message}
          isVisible={true}
          onClose={() => removeError(id)}
          duration={6000}
        />
      ))}
    </>
  )
}
