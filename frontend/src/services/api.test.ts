import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, apiRequest } from '@/services/api'

function stubFetch(impl: (url: string, init: RequestInit) => Promise<Response>) {
  const mock = vi.fn(impl)
  vi.stubGlobal('fetch', mock)
  return mock
}

/** A fetch that never resolves but rejects with AbortError when its signal aborts. */
function hangingFetch() {
  return stubFetch(
    (_url, init) =>
      new Promise<Response>((_resolve, reject) => {
        init.signal?.addEventListener('abort', () =>
          reject(new DOMException('Aborted', 'AbortError')),
        )
      }),
  )
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe('apiRequest', () => {
  it('returns parsed JSON for successful responses', async () => {
    const fetchMock = stubFetch(async () => new Response(JSON.stringify({ a: 1 }), { status: 200 }))

    await expect(apiRequest<{ a: number }>('/x')).resolves.toEqual({ a: 1 })
    expect(fetchMock).toHaveBeenCalledWith(expect.stringMatching(/\/x$/), expect.anything())
  })

  it('maps the backend error envelope to an ApiError', async () => {
    stubFetch(
      async () =>
        new Response(
          JSON.stringify({
            error: {
              code: 'conflict',
              message: 'Already exists',
              details: [{ field: 'name', message: 'taken' }],
            },
          }),
          { status: 409 },
        ),
    )

    const error = await apiRequest('/x').catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({
      status: 409,
      code: 'conflict',
      message: 'Already exists',
      details: [{ field: 'name', message: 'taken' }],
    })
  })

  it('falls back to a generic error when the body is not the envelope', async () => {
    stubFetch(async () => new Response('<html>Bad gateway</html>', { status: 502 }))

    await expect(apiRequest('/x')).rejects.toMatchObject({ status: 502, code: 'http_502' })
  })

  it('reports network failures as ApiError with status 0', async () => {
    stubFetch(async () => {
      throw new TypeError('Failed to fetch')
    })

    await expect(apiRequest('/x')).rejects.toMatchObject({ status: 0, code: 'network_error' })
  })

  it('sends JSON bodies with a Content-Type header', async () => {
    const fetchMock = stubFetch(async () => new Response('{}', { status: 200 }))

    await apiRequest('/x', { method: 'POST', body: { name: 'Ada' } })

    const init = fetchMock.mock.calls[0][1]
    expect(init.method).toBe('POST')
    expect(init.body).toBe(JSON.stringify({ name: 'Ada' }))
    expect(init.headers).toMatchObject({ 'Content-Type': 'application/json' })
  })

  it('propagates caller cancellation as AbortError, not ApiError', async () => {
    hangingFetch()
    const controller = new AbortController()

    const request = apiRequest('/x', { signal: controller.signal })
    controller.abort()

    const error = await request.catch((e: unknown) => e)
    expect(error).not.toBeInstanceOf(ApiError)
    expect(error).toMatchObject({ name: 'AbortError' })
  })

  it('times out slow requests with a timeout ApiError', async () => {
    vi.useFakeTimers()
    hangingFetch()

    const assertion = expect(apiRequest('/x', { timeoutMs: 100 })).rejects.toMatchObject({
      status: 0,
      code: 'timeout',
    })
    await vi.advanceTimersByTimeAsync(100)
    await assertion
  })
})
