// TSS PPM v3.0 - Reviews API
import { get, post, put, getBlob } from './client'

export type ReviewStatus =
  | 'DRAFT'
  | 'PENDING_EMPLOYEE_SIGNATURE'
  | 'PENDING_MANAGER_SIGNATURE'
  | 'SIGNED'
  | 'ARCHIVED'

export type ReviewStage = 'GOAL_SETTING' | 'MID_YEAR_REVIEW' | 'END_YEAR_REVIEW'

export interface ReviewDetails {
  id: string
  employee_id: string
  manager_id: string
  status: ReviewStatus
  stage: ReviewStage
  review_year: number
  tov_level: string | null
  job_title: string | null
  what_score: number | null
  how_score: number | null
  employee_name: string | null
  manager_name: string | null
  employee_signature_date: string | null
  employee_signature_by: string | null
  manager_signature_date: string | null
  manager_signature_by: string | null
  rejection_feedback: string | null
  goal_setting_completed_at: string | null
  mid_year_completed_at: string | null
  end_year_completed_at: string | null
}

export interface ReviewHeaderUpdate {
  job_title?: string
  tov_level?: string
}

export interface SignReviewResponse {
  success: boolean
  message: string
  new_status: ReviewStatus
  signature_date: string
}

export interface RejectReviewResponse {
  success: boolean
  message: string
  new_status: ReviewStatus
}

/**
 * Fetch review details by ID.
 */
export function fetchReview(reviewId: string): Promise<ReviewDetails> {
  return get<ReviewDetails>(`/reviews/${reviewId}`)
}

/**
 * Fetch the current user's review for a given year.
 * Returns null if no review exists.
 */
export async function getReviewForUser(year: number): Promise<ReviewDetails | null> {
  try {
    return await get<ReviewDetails>(`/reviews/me?year=${year}`)
  } catch {
    return null
  }
}

/**
 * Sign a review (as employee or manager).
 */
export function signReview(reviewId: string): Promise<SignReviewResponse> {
  return post<SignReviewResponse>(`/reviews/${reviewId}/sign`, {})
}

/**
 * Reject a review with feedback.
 */
export function rejectReview(
  reviewId: string,
  feedback: string
): Promise<RejectReviewResponse> {
  return post<RejectReviewResponse>(`/reviews/${reviewId}/reject`, { feedback })
}

/**
 * Update review header fields (job_title, tov_level).
 * Only allowed when review is in DRAFT status.
 */
export function updateReviewHeader(
  reviewId: string,
  data: ReviewHeaderUpdate
): Promise<ReviewDetails> {
  return put<ReviewDetails>(`/reviews/${reviewId}`, data)
}

/**
 * Download review as PDF.
 * @param reviewId - The review ID
 * @param lang - Language code (en, nl, es)
 * @returns PDF file as Blob
 */
export function downloadReviewPdf(reviewId: string, lang: string = 'en'): Promise<Blob> {
  return getBlob(`/reviews/${reviewId}/pdf?lang=${lang}`)
}

export interface ManagerReassignResponse {
  id: string
  employee_id: string
  manager_id: string
  status: string
  stage: string
  review_year: number
  job_title: string | null
  tov_level: string | null
}

/**
 * Reassign a review to a different manager.
 * Only HR users can perform this action.
 * @param reviewId - The review ID
 * @param newManagerId - The new manager's user ID
 * @param reason - Optional reason for the reassignment
 */
export function reassignManager(
  reviewId: string,
  newManagerId: string,
  reason?: string
): Promise<ManagerReassignResponse> {
  const payload: { new_manager_id: string; reason?: string } = {
    new_manager_id: newManagerId,
  }
  if (reason) {
    payload.reason = reason
  }
  return put<ManagerReassignResponse>(`/reviews/${reviewId}/manager`, payload)
}

// --- Stage Transition API ---

export interface StageTransitionResponse {
  id: string
  old_stage: string
  new_stage: string
  status: string
}

export interface BulkStageAdvanceRequest {
  from_stage: ReviewStage
  review_year?: number
}

export interface BulkStageAdvanceResponse {
  advanced_count: number
  skipped_count: number
  from_stage: string
  to_stage: string
  review_ids: string[]
}

/**
 * Advance a single review to the next stage.
 * Only HR users can perform this action.
 * Review must be in SIGNED status.
 * @param reviewId - The review ID
 */
export function advanceReviewStage(reviewId: string): Promise<StageTransitionResponse> {
  return post<StageTransitionResponse>(`/reviews/${reviewId}/advance-stage`, {})
}

/**
 * Bulk advance all eligible reviews in the OpCo to the next stage.
 * Only HR users can perform this action.
 * @param request - The bulk advance request with from_stage and optional year filter
 */
export function bulkAdvanceStage(
  request: BulkStageAdvanceRequest
): Promise<BulkStageAdvanceResponse> {
  return post<BulkStageAdvanceResponse>('/hr/reviews/advance-stage', request)
}

/**
 * Get human-readable stage name.
 */
export function getStageName(stage: ReviewStage): string {
  const stageNames: Record<ReviewStage, string> = {
    GOAL_SETTING: 'Goal Setting',
    MID_YEAR_REVIEW: 'Mid-Year Review',
    END_YEAR_REVIEW: 'End-Year Review',
  }
  return stageNames[stage] || stage
}

/**
 * Get the next stage in the progression.
 */
export function getNextStage(stage: ReviewStage): ReviewStage | 'ARCHIVED' | null {
  const stageOrder: Record<ReviewStage, ReviewStage | 'ARCHIVED'> = {
    GOAL_SETTING: 'MID_YEAR_REVIEW',
    MID_YEAR_REVIEW: 'END_YEAR_REVIEW',
    END_YEAR_REVIEW: 'ARCHIVED',
  }
  return stageOrder[stage] || null
}
