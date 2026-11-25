import { env } from '@/lib/env'

export interface ApiErrorDetail {
  field: string
  message: string
}

/** Error thrown for any failed API call. `status` is 0 when no HTTP response was received. */
export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details: ApiErrorDetail[]

  constructor(status: number, code: string, message: string, details: ApiErrorDetail[] = []) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

export interface ApiRequestOptions {
  method?: string
  /** Serialised as JSON when provided. */
  body?: unknown
  headers?: Record<string, string>
  /** Caller cancellation; an aborted call rejects with the browser's AbortError, not ApiError. */
  signal?: AbortSignal
  timeoutMs?: number
}

const DEFAULT_TIMEOUT_MS = 15_000

function parseDetails(value: unknown): ApiErrorDetail[] {
  if (!Array.isArray(value)) return []
  return value.filter(
    (item): item is ApiErrorDetail =>
      typeof item === 'object' &&
      item !== null &&
      typeof (item as ApiErrorDetail).field === 'string' &&
      typeof (item as ApiErrorDetail).message === 'string',
  )
}

/** Maps the backend's `{error: {code, message, details}}` envelope to an ApiError. */
function toApiError(status: number, payload: unknown): ApiError {
  const error = (payload as { error?: { code?: unknown; message?: unknown; details?: unknown } } | undefined)
    ?.error
  if (error && typeof error.code === 'string' && typeof error.message === 'string') {
    return new ApiError(status, error.code, error.message, parseDetails(error.details))
  }
  return new ApiError(status, `http_${status}`, 'The request failed')
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { body, headers, signal, method, timeoutMs = DEFAULT_TIMEOUT_MS } = options

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  const forwardAbort = () => controller.abort()
  signal?.addEventListener('abort', forwardAbort, { once: true })
  if (signal?.aborted) controller.abort()

  try {
    let response: Response
    try {
      response = await fetch(`${env.VITE_API_BASE_URL}${path}`, {
        method,
        headers: {
          Accept: 'application/json',
          ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
          ...headers,
        },
        body: body !== undefined ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      })
    } catch (err) {
      if (signal?.aborted) throw err // the caller cancelled; let them handle AbortError
      if (controller.signal.aborted) {
        throw new ApiError(0, 'timeout', 'The server took too long to respond')
      }
      throw new ApiError(0, 'network_error', 'Unable to reach the server')
    }

    const text = await response.text()
    let payload: unknown
    if (text) {
      try {
        payload = JSON.parse(text)
      } catch {
        payload = undefined
      }
    }

    if (!response.ok) throw toApiError(response.status, payload)
    return payload as T
  } finally {
    clearTimeout(timer)
    signal?.removeEventListener('abort', forwardAbort)
  }
}
