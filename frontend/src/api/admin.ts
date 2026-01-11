// TSS PPM v3.0 - Admin API
import { get, put, post } from './client'

export interface AdminUser {
  id: string
  email: string
  first_name: string | null
  last_name: string | null
  enabled: boolean
  roles: string[]
  function_title: string | null
  tov_level: string | null
  manager_id: string | null
  opco_id: string | null
}

export interface UpdateRolesRequest {
  roles: string[]
}

export interface UpdateManagerRequest {
  manager_id: string
}

export interface UpdateStatusRequest {
  enabled: boolean
}

export interface BulkOperationRequest {
  user_ids: string[]
  operation: 'assign_role' | 'remove_role' | 'assign_manager'
  role?: string
  manager_id?: string
}

export interface BulkOperationResponse {
  processed: number
  failed: number
  errors: string[]
}

export interface ListUsersParams {
  search?: string
  role?: string
  enabled?: boolean
  first?: number
  max_results?: number
}

/**
 * Fetch list of users with optional filters.
 */
export async function fetchUsers(params: ListUsersParams = {}): Promise<AdminUser[]> {
  const queryParams = new URLSearchParams()
  if (params.search) queryParams.set('search', params.search)
  if (params.role) queryParams.set('role', params.role)
  if (params.enabled !== undefined) queryParams.set('enabled', String(params.enabled))
  if (params.first !== undefined) queryParams.set('first', String(params.first))
  if (params.max_results !== undefined) queryParams.set('max_results', String(params.max_results))

  const query = queryParams.toString()
  return get<AdminUser[]>(`/admin/users${query ? `?${query}` : ''}`)
}

/**
 * Fetch a single user by ID.
 */
export function fetchUser(userId: string): Promise<AdminUser> {
  return get<AdminUser>(`/admin/users/${userId}`)
}

/**
 * Update a user's roles.
 */
export function updateUserRoles(userId: string, roles: string[]): Promise<{ message: string }> {
  return put<{ message: string }>(`/admin/users/${userId}/roles`, { roles })
}

/**
 * Update a user's manager.
 */
export function updateUserManager(userId: string, managerId: string): Promise<{ message: string }> {
  return put<{ message: string }>(`/admin/users/${userId}/manager`, { manager_id: managerId })
}

/**
 * Enable or disable a user.
 */
export function updateUserStatus(userId: string, enabled: boolean): Promise<{ message: string }> {
  return put<{ message: string }>(`/admin/users/${userId}/status`, { enabled })
}

/**
 * Perform bulk operations on multiple users.
 */
export function bulkOperation(request: BulkOperationRequest): Promise<BulkOperationResponse> {
  return post<BulkOperationResponse>('/admin/users/bulk', request)
}

/**
 * Fetch list of managers for dropdown selection.
 */
export async function fetchManagers(): Promise<AdminUser[]> {
  // Filter users who have manager role
  return fetchUsers({ role: 'manager' })
}
