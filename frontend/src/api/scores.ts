// TSS PPM v3.0 - Scores API Client
import { get, put, post } from './client'

// Response types (what the API returns)
export interface GoalScoreResponse {
  id: string
  review_id: string
  title: string
  description?: string
  goal_type: string
  weight: number
  score: number | null
  feedback?: string
  display_order: number
}

export interface CompetencyScoreResponse {
  id: string
  review_id: string
  competency_id: string
  score: number | null
  notes?: string
  category: string
  subcategory: string
  title_en: string
  display_order: number
}

export interface AllScoresResponse {
  goal_scores: GoalScoreResponse[]
  competency_scores: CompetencyScoreResponse[]
}

// Request types (what we send to the API)
export interface GoalScoreUpdate {
  goal_id: string
  score?: number | null
  feedback?: string
}

export interface CompetencyScoreUpdate {
  competency_id: string
  score?: number | null
  notes?: string
}

export interface ScoresUpdateRequest {
  goal_scores?: GoalScoreUpdate[]
  competency_scores?: CompetencyScoreUpdate[]
}

export interface SubmitResponse {
  status: string
}

export interface ScoresUpdateResponse {
  message: string
  updated_goals: number
  updated_competencies: number
}

/**
 * Fetch scores for a review
 */
export function fetchScores(reviewId: string): Promise<AllScoresResponse> {
  return get<AllScoresResponse>(`/reviews/${reviewId}/scores`)
}

/**
 * Save scores for a review (partial or full)
 * Filters out entries that have nothing to save (no score and no feedback)
 */
export function saveScores(reviewId: string, request: ScoresUpdateRequest): Promise<ScoresUpdateResponse> {
  // Filter to only include entries that have something to save
  // Goals: need either a score OR feedback
  // Competencies: need a score (notes alone aren't saved without score)
  const filteredRequest: ScoresUpdateRequest = {
    goal_scores: (request.goal_scores || []).filter(gs =>
      (gs.score !== null && gs.score !== undefined) ||
      (gs.feedback !== null && gs.feedback !== undefined && gs.feedback !== '')
    ),
    competency_scores: (request.competency_scores || []).filter(cs =>
      cs.score !== null && cs.score !== undefined
    ),
  }

  // Don't make the request if there's nothing to save
  if (
    (!filteredRequest.goal_scores || filteredRequest.goal_scores.length === 0) &&
    (!filteredRequest.competency_scores || filteredRequest.competency_scores.length === 0)
  ) {
    return Promise.resolve({ message: 'No changes to save', updated_goals: 0, updated_competencies: 0 })
  }

  return put<ScoresUpdateResponse>(`/reviews/${reviewId}/scores`, filteredRequest)
}

/**
 * Submit scores for a review (transitions status to PENDING_EMPLOYEE_SIGNATURE)
 */
export function submitScores(reviewId: string): Promise<SubmitResponse> {
  return post<SubmitResponse>(`/reviews/${reviewId}/submit-scores`, {})
}
