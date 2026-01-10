// TSS PPM v3.0 - API Client Tests
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { apiRequest, get, post, put, del, ApiRequestError } from '../api/client'

// Mock the auth module
vi.mock('../api/auth', () => ({
  getToken: vi.fn().mockResolvedValue('test-token'),
}))

describe('API Client', () => {
  const mockFetch = vi.fn()

  beforeEach(() => {
    vi.stubGlobal('fetch', mockFetch)
    mockFetch.mockReset()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  describe('apiRequest', () => {
    it('should add authorization header with token', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: 'test' }),
      })

      await apiRequest('/test')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json',
          }),
        })
      )
    })

    it('should return JSON data on success', async () => {
      const responseData = { id: '123', name: 'Test' }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve(responseData),
      })

      const result = await apiRequest('/test')

      expect(result).toEqual(responseData)
    })

    it('should handle 204 No Content response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
      })

      const result = await apiRequest('/test', { method: 'DELETE' })

      expect(result).toBeUndefined()
    })

    it('should throw ApiRequestError on 404', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: () => Promise.resolve({ detail: 'Resource not found' }),
      })

      await expect(apiRequest('/test')).rejects.toMatchObject({
        status: 404,
        detail: 'Resource not found',
      })
    })

    it('should throw ApiRequestError on 400', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: () => Promise.resolve({ detail: 'Validation error' }),
      })

      await expect(apiRequest('/test')).rejects.toThrow(ApiRequestError)
    })

    it('should handle non-JSON error responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.reject(new Error('Not JSON')),
      })

      await expect(apiRequest('/test')).rejects.toThrow(ApiRequestError)
    })
  })

  describe('HTTP method helpers', () => {
    it('get() should make GET request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve([]),
      })

      await get('/items')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({ method: 'GET' })
      )
    })

    it('post() should make POST request with body', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: () => Promise.resolve({ id: '1' }),
      })

      await post('/items', { name: 'New Item' })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ name: 'New Item' }),
        })
      )
    })

    it('put() should make PUT request with body', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ id: '1', name: 'Updated' }),
      })

      await put('/items/1', { name: 'Updated' })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ name: 'Updated' }),
        })
      )
    })

    it('del() should make DELETE request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
      })

      await del('/items/1')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({ method: 'DELETE' })
      )
    })
  })
})
