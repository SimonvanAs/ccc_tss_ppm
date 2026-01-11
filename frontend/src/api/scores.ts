// TSS PPM v3.0 - Scores API Client
import { get, put, post } from './client'

export interface GoalScoreData {
  goal_id: string
  score: number | null
  feedback?: string
}

export interface CompetencyScoreData {
  competency_id: string
  score: number | null
}

export interface ScoresData {
  goal_scores: GoalScoreData[]
  competency_scores: CompetencyScoreData[]
}

export interface SubmitResponse {
  status: string
}

/**
 * Fetch scores for a review
 */
export function fetchScores(reviewId: string): Promise<ScoresData> {
  return get<ScoresData>(`/reviews/${reviewId}/scores`)
}

/**
 * Save scores for a review (partial or full)
 */
export function saveScores(reviewId: string, scores: ScoresData): Promise<ScoresData> {
  return put<ScoresData>(`/reviews/${reviewId}/scores`, scores)
}

/**
 * Submit scores for a review (transitions status to PENDING_EMPLOYEE_SIGNATURE)
 */
export function submitScores(reviewId: string): Promise<SubmitResponse> {
  return post<SubmitResponse>(`/reviews/${reviewId}/submit-scores`, {})
}
