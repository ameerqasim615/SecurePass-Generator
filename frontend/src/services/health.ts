import { z } from 'zod'
import { ApiError, apiRequest } from '@/services/api'

const healthSchema = z.object({
  status: z.literal('ok'),
  service: z.string(),
  version: z.string(),
})

export type HealthResponse = z.infer<typeof healthSchema>

export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const data = await apiRequest<unknown>('/api/v1/health', { signal })
  const parsed = healthSchema.safeParse(data)
  if (!parsed.success) {
    throw new ApiError(502, 'invalid_response', 'The server returned an unexpected response')
  }
  return parsed.data
}
