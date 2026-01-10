// TSS PPM v3.0 - Review Type Definitions

/**
 * Review workflow stages.
 */
export enum ReviewStage {
  GOAL_SETTING = 'GOAL_SETTING',
  MID_YEAR_REVIEW = 'MID_YEAR_REVIEW',
  END_YEAR_REVIEW = 'END_YEAR_REVIEW',
}

/**
 * Review status values.
 */
export enum ReviewStatus {
  DRAFT = 'DRAFT',
  PENDING_EMPLOYEE_SIGNATURE = 'PENDING_EMPLOYEE_SIGNATURE',
  EMPLOYEE_SIGNED = 'EMPLOYEE_SIGNED',
  PENDING_MANAGER_SIGNATURE = 'PENDING_MANAGER_SIGNATURE',
  MANAGER_SIGNED = 'MANAGER_SIGNED',
  SIGNED = 'SIGNED',
  ARCHIVED = 'ARCHIVED',
}

/**
 * Review as returned from the API.
 */
export interface Review {
  id: string
  employee_id: string
  manager_id: string
  status: ReviewStatus
  stage: ReviewStage
  review_year: number
  what_score: number | null
  how_score: number | null
}
