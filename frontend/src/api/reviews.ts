// TSS PPM v3.0 - Reviews API
import { get, post, put } from './client'

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
