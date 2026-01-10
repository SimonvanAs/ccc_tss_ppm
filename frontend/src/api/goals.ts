// TSS PPM v3.0 - Goals API
import { get, post, put, del } from './client'
import type { Goal, GoalCreate, GoalUpdate, GoalOrderRequest } from '../types'

/**
 * Fetch all goals for a review.
 */
export function fetchGoals(reviewId: string): Promise<Goal[]> {
  return get<Goal[]>(`/reviews/${reviewId}/goals`)
}

/**
 * Create a new goal.
 */
export function createGoal(reviewId: string, data: GoalCreate): Promise<Goal> {
  return post<Goal>(`/reviews/${reviewId}/goals`, data)
}

/**
 * Update an existing goal.
 */
export function updateGoal(goalId: string, data: GoalUpdate): Promise<Goal> {
  return put<Goal>(`/goals/${goalId}`, data)
}

/**
 * Delete a goal.
 */
export function deleteGoal(goalId: string): Promise<void> {
  return del<void>(`/goals/${goalId}`)
}

/**
 * Reorder goals.
 */
export function reorderGoals(reviewId: string, goalIds: string[]): Promise<void> {
  return put<void>(`/reviews/${reviewId}/goals/order`, { goal_ids: goalIds } as GoalOrderRequest)
}

/**
 * Submit a review after goal setting.
 */
export function submitReview(reviewId: string): Promise<void> {
  return post<void>(`/reviews/${reviewId}/submit`)
}
