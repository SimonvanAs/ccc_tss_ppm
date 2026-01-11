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

/**
 * Team member with 9-grid position data for grid visualization.
 */
export interface TeamMemberGrid {
  id: string
  email: string
  first_name: string | null
  last_name: string | null
  review_id: string | null
  review_status: string | null
  what_score: number | null
  how_score: number | null
  grid_position_what: number | null
  grid_position_how: number | null
  what_veto_active: boolean
  how_veto_active: boolean
}
