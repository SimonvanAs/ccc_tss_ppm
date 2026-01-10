// TSS PPM v3.0 - Goal Type Definitions

/**
 * Goal types with their scoring implications.
 * - STANDARD: Normal goal, contributes to weighted average
 * - KAR: Key Area of Responsibility - VETO potential if score=1
 * - SCF: Strategic Critical Focus - VETO if score=1
 */
export enum GoalType {
  STANDARD = 'STANDARD',
  KAR = 'KAR',
  SCF = 'SCF',
}

/**
 * Goal as returned from the API.
 */
export interface Goal {
  id: string
  review_id: string
  title: string
  description: string | null
  goal_type: GoalType
  weight: number
  score: number | null
  display_order: number
}

/**
 * Data for creating a new goal.
 */
export interface GoalCreate {
  title: string
  description?: string | null
  goal_type?: GoalType
  weight: number
}

/**
 * Data for updating an existing goal.
 */
export interface GoalUpdate {
  title?: string
  description?: string | null
  goal_type?: GoalType
  weight?: number
}

/**
 * Request body for reordering goals.
 */
export interface GoalOrderRequest {
  goal_ids: string[]
}
