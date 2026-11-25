import { CircleAlert, CircleCheck, LoaderCircle, RefreshCw } from 'lucide-react'
import { useBackendHealth } from '@/hooks/useBackendHealth'

/**
 * Phase 1 shell. The landing page replaces this in Phase 2; the live backend
 * connection check stays useful for verifying deployments.
 */
export function HomePage() {
  const { state, retry } = useBackendHealth()

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4 dark:bg-slate-950">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <h1 className="text-2xl font-semibold text-navy-800 dark:text-white">
          Resume<span className="text-violet-600 dark:text-violet-400">AI</span>
        </h1>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
          Smart AI Resume Builder - project foundation. Product pages arrive in the next phases.
        </p>

        <section aria-labelledby="backend-status" className="mt-6">
          <h2 id="backend-status" className="text-sm font-medium text-slate-900 dark:text-slate-100">
            Backend connection
          </h2>

          <div role="status" className="mt-2 flex items-start gap-3 text-sm">
            {state.status === 'loading' && (
              <>
                <LoaderCircle className="mt-0.5 h-4 w-4 animate-spin text-slate-500" aria-hidden />
                <span className="text-slate-600 dark:text-slate-400">Checking the API...</span>
              </>
            )}

            {state.status === 'ok' && (
              <>
                <CircleCheck className="mt-0.5 h-4 w-4 text-emerald-600" aria-hidden />
                <span className="text-slate-700 dark:text-slate-300">
                  Connected to {state.data.service} v{state.data.version}
                </span>
              </>
            )}

            {state.status === 'error' && (
              <>
                <CircleAlert className="mt-0.5 h-4 w-4 text-red-600" aria-hidden />
                <div className="flex-1">
                  <p className="text-slate-700 dark:text-slate-300">{state.message}</p>
                  <button
                    type="button"
                    onClick={retry}
                    className="mt-2 inline-flex items-center gap-1.5 rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 transition-colors hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
                  >
                    <RefreshCw className="h-3.5 w-3.5" aria-hidden />
                    Try again
                  </button>
                </div>
              </>
            )}
          </div>
        </section>
      </div>
    </main>
  )
}
