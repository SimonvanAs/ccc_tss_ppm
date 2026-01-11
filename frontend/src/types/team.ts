// TSS PPM v3.0 - Team Types

/**
 * Scoring status for a team member's review.
 */
export enum ScoringStatus {
  NOT_STARTED = 'NOT_STARTED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETE = 'COMPLETE',
}

/**
 * Team member response from the API.
 */
export interface TeamMember {
  id: string
  email: string
  first_name: string | null
  last_name: string | null
  function_title: string | null
  tov_level: string | null
  review_id: string | null
  review_stage: string | null
  review_status: string | null
  scoring_status: ScoringStatus
}
