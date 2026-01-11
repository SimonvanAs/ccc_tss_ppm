// TSS PPM v3.0 - Reviews API
import { get } from './client'

export interface ReviewDetails {
  id: string
  employee_id: string
  manager_id: string
  status: string
  stage: string
  review_year: number
  tov_level: string | null
  job_title: string | null
  what_score: number | null
  how_score: number | null
  employee_name: string | null
  manager_name: string | null
}

/**
 * Fetch review details by ID.
 */
export function fetchReview(reviewId: string): Promise<ReviewDetails> {
  return get<ReviewDetails>(`/reviews/${reviewId}`)
}
