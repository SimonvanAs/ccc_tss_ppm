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
 * Filters out entries that have nothing to save (no score and no feedback)
 */
export function saveScores(reviewId: string, scores: ScoresData): Promise<ScoresData> {
  // Filter to only include entries that have something to save
  // Goals: need either a score OR feedback
  // Competencies: need a score (notes alone aren't saved without score)
  const filteredScores = {
    goal_scores: scores.goal_scores.filter(gs =>
      gs.score !== null && gs.score !== undefined ||
      gs.feedback !== null && gs.feedback !== undefined && gs.feedback !== ''
    ),
    competency_scores: scores.competency_scores.filter(cs =>
      cs.score !== null && cs.score !== undefined
    ),
  }

  // Don't make the request if there's nothing to save
  if (filteredScores.goal_scores.length === 0 && filteredScores.competency_scores.length === 0) {
    return Promise.resolve({ goal_scores: [], competency_scores: [] })
  }

  return put<ScoresData>(`/reviews/${reviewId}/scores`, filteredScores)
}

/**
 * Submit scores for a review (transitions status to PENDING_EMPLOYEE_SIGNATURE)
 */
export function submitScores(reviewId: string): Promise<SubmitResponse> {
  return post<SubmitResponse>(`/reviews/${reviewId}/submit-scores`, {})
}
