// TSS PPM v3.0 - Admin API
import { get, put, post, del } from './client'

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

// ===== OpCo Settings =====

export interface ReviewCycleSettings {
  goal_setting_start: string
  goal_setting_end: string
  mid_year_start: string
  mid_year_end: string
  end_year_start: string
  end_year_end: string
}

export interface OpCoSettings {
  review_cycle?: ReviewCycleSettings
}

export interface OpCoResponse {
  id: string
  name: string
  code: string
  logo_url: string | null
  default_language: string
  settings: OpCoSettings
}

export interface OpCoUpdateRequest {
  name?: string
  code?: string
  logo_url?: string | null
  default_language?: string
  settings?: OpCoSettings
}

/**
 * Fetch current OpCo settings.
 */
export function fetchOpCoSettings(): Promise<OpCoResponse> {
  return get<OpCoResponse>('/admin/opco/settings')
}

/**
 * Update OpCo settings.
 */
export function updateOpCoSettings(data: OpCoUpdateRequest): Promise<OpCoResponse> {
  return put<OpCoResponse>('/admin/opco/settings', data)
}

// ===== Business Units =====

export interface BusinessUnit {
  id: string
  name: string
  code: string
  parent_id: string | null
  opco_id: string
}

export interface BusinessUnitCreateRequest {
  name: string
  code: string
  parent_id?: string | null
}

export interface BusinessUnitUpdateRequest {
  name?: string
  code?: string
  parent_id?: string | null
}

/**
 * Fetch list of business units.
 */
export function fetchBusinessUnits(): Promise<BusinessUnit[]> {
  return get<BusinessUnit[]>('/admin/business-units')
}

/**
 * Create a new business unit.
 */
export function createBusinessUnit(data: BusinessUnitCreateRequest): Promise<BusinessUnit> {
  return post<BusinessUnit>('/admin/business-units', data)
}

/**
 * Update a business unit.
 */
export function updateBusinessUnit(id: string, data: BusinessUnitUpdateRequest): Promise<BusinessUnit> {
  return put<BusinessUnit>(`/admin/business-units/${id}`, data)
}

/**
 * Delete a business unit.
 */
export function deleteBusinessUnit(id: string): Promise<void> {
  return del<void>(`/admin/business-units/${id}`)
}
