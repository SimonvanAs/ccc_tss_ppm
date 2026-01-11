// TSS PPM v3.0 - API Client with Authentication
import { getToken } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export interface ApiError {
  status: number
  message: string
  detail?: string
}

export class ApiRequestError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail)
    this.name = 'ApiRequestError'
  }
}

/**
 * Make an authenticated API request.
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getToken()

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const url = `${API_BASE_URL}${endpoint}`

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    let detail = `HTTP ${response.status}: ${response.statusText}`
    try {
      const errorData = await response.json()
      detail = errorData.detail || detail
    } catch {
      // Ignore JSON parse errors
    }
    throw new ApiRequestError(response.status, detail)
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

/**
 * GET request helper.
 */
export function get<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, { method: 'GET' })
}

/**
 * POST request helper.
 */
export function post<T>(endpoint: string, data?: unknown): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  })
}

/**
 * PUT request helper.
 */
export function put<T>(endpoint: string, data?: unknown): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  })
}

/**
 * DELETE request helper.
 */
export function del<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, { method: 'DELETE' })
}

/**
 * GET request helper that returns a Blob (for file downloads).
 */
export async function getBlob(endpoint: string): Promise<Blob> {
  const token = await getToken()

  const headers: HeadersInit = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const url = `${API_BASE_URL}${endpoint}`

  const response = await fetch(url, {
    method: 'GET',
    headers,
  })

  if (!response.ok) {
    let detail = `HTTP ${response.status}: ${response.statusText}`
    try {
      const errorData = await response.json()
      detail = errorData.detail || detail
    } catch {
      // Ignore JSON parse errors
    }
    throw new ApiRequestError(response.status, detail)
  }

  return response.blob()
}
