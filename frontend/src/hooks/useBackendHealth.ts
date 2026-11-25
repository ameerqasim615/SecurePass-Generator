import { useCallback, useEffect, useState } from 'react'
import { ApiError } from '@/services/api'
import { getHealth, type HealthResponse } from '@/services/health'

export type BackendHealthState =
  | { status: 'loading' }
  | { status: 'ok'; data: HealthResponse }
  | { status: 'error'; message: string }

/** Checks the FastAPI backend once on mount; `retry` re-runs the check. */
export function useBackendHealth() {
  const [state, setState] = useState<BackendHealthState>({ status: 'loading' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    setState({ status: 'loading' })

    getHealth(controller.signal)
      .then((data) => setState({ status: 'ok', data }))
      .catch((error: unknown) => {
        if (controller.signal.aborted) return
        setState({
          status: 'error',
          message: error instanceof ApiError ? error.message : 'Something went wrong',
        })
      })

    return () => controller.abort()
  }, [attempt])

  const retry = useCallback(() => setAttempt((n) => n + 1), [])
  return { state, retry }
}
