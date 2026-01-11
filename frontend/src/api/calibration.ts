// TSS PPM v3.0 - Calibration Sessions API
import { get, post, put, del } from './client'

export type CalibrationSessionStatus =
  | 'PREPARATION'
  | 'IN_PROGRESS'
  | 'PENDING_APPROVAL'
  | 'COMPLETED'
  | 'CANCELLED'

export type CalibrationScope = 'BUSINESS_UNIT' | 'COMPANY_WIDE'

export interface CalibrationSession {
  id: string
  opco_id: string
  name: string
  description: string | null
  review_year: number
  scope: CalibrationScope
  business_unit_id: string | null
  status: CalibrationSessionStatus
  facilitator_id: string | null
  created_by: string | null
  snapshot_taken_at: string | null
  completed_at: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface CalibrationSessionCreate {
  name: string
  description?: string
  review_year: number
  scope: CalibrationScope
  business_unit_id?: string
  facilitator_id?: string
}

export interface CalibrationSessionUpdate {
  name?: string
  description?: string
  facilitator_id?: string
  notes?: string
}

export interface CalibrationReview {
  review_id: string
  employee_id: string
  employee_name: string
  employee_email: string | null
  what_score: number | null
  how_score: number | null
  grid_position_what: number | null
  grid_position_how: number | null
  what_veto_active: boolean
  how_veto_active: boolean
  review_status: string | null
  manager_first_name: string | null
  manager_last_name: string | null
}

export interface CalibrationParticipant {
  user_id: string
  role: 'FACILITATOR' | 'PARTICIPANT' | 'OBSERVER'
  first_name: string | null
  last_name: string | null
  email: string | null
}

export interface CalibrationNote {
  id: string
  session_id: string
  review_id: string | null
  content: string
  created_by: string
  first_name: string | null
  last_name: string | null
  created_at: string
}

export interface ScoreAdjustment {
  adjustment_id: string
  session_id: string
  review_id: string
  adjusted_by: string
  original_what_score: number | null
  original_how_score: number | null
  what_score: number | null
  how_score: number | null
  rationale: string
  created_at: string
  adjuster_first_name: string | null
  adjuster_last_name: string | null
}

export interface AdjustmentHistory {
  id: string
  session_id: string
  review_id: string
  adjusted_by: string
  original_what_score: number | null
  original_how_score: number | null
  adjusted_what_score: number | null
  adjusted_how_score: number | null
  adjustment_notes: string | null
  created_at: string
  adjuster_first_name: string | null
  adjuster_last_name: string | null
}

// --- Session CRUD ---

/**
 * Fetch all calibration sessions.
 */
export function fetchCalibrationSessions(params?: {
  status?: CalibrationSessionStatus
  review_year?: number
}): Promise<CalibrationSession[]> {
  const searchParams = new URLSearchParams()
  if (params?.status) searchParams.append('status', params.status)
  if (params?.review_year) searchParams.append('review_year', params.review_year.toString())
  const query = searchParams.toString()
  return get<CalibrationSession[]>(`/calibration-sessions${query ? `?${query}` : ''}`)
}

/**
 * Fetch a single calibration session by ID.
 */
export function fetchCalibrationSession(sessionId: string): Promise<CalibrationSession> {
  return get<CalibrationSession>(`/calibration-sessions/${sessionId}`)
}

/**
 * Create a new calibration session.
 */
export function createCalibrationSession(
  data: CalibrationSessionCreate
): Promise<CalibrationSession> {
  return post<CalibrationSession>('/calibration-sessions', data)
}

/**
 * Update a calibration session.
 */
export function updateCalibrationSession(
  sessionId: string,
  data: CalibrationSessionUpdate
): Promise<CalibrationSession> {
  return put<CalibrationSession>(`/calibration-sessions/${sessionId}`, data)
}

/**
 * Delete a calibration session (only PREPARATION status).
 */
export function deleteCalibrationSession(sessionId: string): Promise<void> {
  return del(`/calibration-sessions/${sessionId}`)
}

// --- Status Transitions ---

/**
 * Start a calibration session (PREPARATION -> IN_PROGRESS).
 */
export function startCalibrationSession(sessionId: string): Promise<CalibrationSession> {
  return post<CalibrationSession>(`/calibration-sessions/${sessionId}/start`, {})
}

/**
 * Complete a calibration session.
 */
export function completeCalibrationSession(sessionId: string): Promise<CalibrationSession> {
  return post<CalibrationSession>(`/calibration-sessions/${sessionId}/complete`, {})
}

// --- Reviews ---

/**
 * Fetch reviews in a calibration session.
 */
export function fetchSessionReviews(sessionId: string): Promise<CalibrationReview[]> {
  return get<CalibrationReview[]>(`/calibration-sessions/${sessionId}/reviews`)
}

/**
 * Add a review to a session.
 */
export function addReviewToSession(
  sessionId: string,
  reviewId: string
): Promise<{ status: string }> {
  return post<{ status: string }>(`/calibration-sessions/${sessionId}/reviews/${reviewId}`, {})
}

/**
 * Remove a review from a session.
 */
export function removeReviewFromSession(sessionId: string, reviewId: string): Promise<void> {
  return del(`/calibration-sessions/${sessionId}/reviews/${reviewId}`)
}

// --- Score Adjustments ---

/**
 * Adjust review scores during calibration.
 */
export function adjustReviewScores(
  sessionId: string,
  reviewId: string,
  data: { what_score?: number; how_score?: number; rationale: string }
): Promise<ScoreAdjustment> {
  return put<ScoreAdjustment>(
    `/calibration-sessions/${sessionId}/reviews/${reviewId}/scores`,
    data
  )
}

/**
 * Get adjustment history for a review.
 */
export function fetchAdjustmentHistory(
  sessionId: string,
  reviewId: string
): Promise<AdjustmentHistory[]> {
  return get<AdjustmentHistory[]>(
    `/calibration-sessions/${sessionId}/reviews/${reviewId}/adjustments`
  )
}

// --- Participants ---

/**
 * Fetch participants in a session.
 */
export function fetchSessionParticipants(sessionId: string): Promise<CalibrationParticipant[]> {
  return get<CalibrationParticipant[]>(`/calibration-sessions/${sessionId}/participants`)
}

/**
 * Add a participant to a session.
 */
export function addParticipant(
  sessionId: string,
  userId: string,
  role: 'FACILITATOR' | 'PARTICIPANT' | 'OBSERVER'
): Promise<CalibrationParticipant> {
  return post<CalibrationParticipant>(`/calibration-sessions/${sessionId}/participants`, {
    user_id: userId,
    role,
  })
}

/**
 * Remove a participant from a session.
 */
export function removeParticipant(sessionId: string, userId: string): Promise<void> {
  return del(`/calibration-sessions/${sessionId}/participants/${userId}`)
}

// --- Notes ---

/**
 * Fetch notes for a session.
 */
export function fetchSessionNotes(
  sessionId: string,
  reviewId?: string
): Promise<CalibrationNote[]> {
  const query = reviewId ? `?review_id=${reviewId}` : ''
  return get<CalibrationNote[]>(`/calibration-sessions/${sessionId}/notes${query}`)
}

/**
 * Add a note to a session.
 */
export function addNote(
  sessionId: string,
  content: string,
  reviewId?: string
): Promise<CalibrationNote> {
  return post<CalibrationNote>(`/calibration-sessions/${sessionId}/notes`, {
    content,
    review_id: reviewId,
  })
}
