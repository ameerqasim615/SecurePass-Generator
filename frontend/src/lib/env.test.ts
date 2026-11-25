import { describe, expect, it } from 'vitest'
import { parseEnv } from '@/lib/env'

describe('parseEnv', () => {
  it('falls back to the local backend URL when unset', () => {
    expect(parseEnv({}).VITE_API_BASE_URL).toBe('http://localhost:8000')
  })

  it('treats an empty value as unset', () => {
    expect(parseEnv({ VITE_API_BASE_URL: '' }).VITE_API_BASE_URL).toBe('http://localhost:8000')
  })

  it('strips trailing slashes', () => {
    expect(parseEnv({ VITE_API_BASE_URL: 'https://api.example.com//' }).VITE_API_BASE_URL).toBe(
      'https://api.example.com',
    )
  })

  it('rejects an invalid URL with a readable message', () => {
    expect(() => parseEnv({ VITE_API_BASE_URL: 'not-a-url' })).toThrow(/VITE_API_BASE_URL/)
  })
})
