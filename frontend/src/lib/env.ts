import { z } from 'zod'

const DEFAULT_API_BASE_URL = 'http://localhost:8000'

const envSchema = z.object({
  VITE_API_BASE_URL: z.preprocess(
    // An empty variable (`VITE_API_BASE_URL=`) means "not set".
    (value) => (value === '' ? undefined : value),
    z
      .string()
      .url('must be a valid URL, e.g. http://localhost:8000')
      .default(DEFAULT_API_BASE_URL)
      .transform((url) => url.replace(/\/+$/, '')),
  ),
})

export type Env = z.infer<typeof envSchema>

/** Validates raw env values; throws a readable error so misconfiguration fails fast. */
export function parseEnv(raw: Record<string, unknown>): Env {
  const result = envSchema.safeParse(raw)
  if (!result.success) {
    const problems = result.error.issues
      .map((issue) => `${issue.path.join('.') || 'env'}: ${issue.message}`)
      .join('; ')
    throw new Error(`Invalid frontend environment configuration - ${problems}`)
  }
  return result.data
}

export const env = parseEnv(import.meta.env)
