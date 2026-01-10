// TSS PPM v3.0 - Goals API Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchGoals, createGoal, updateGoal, deleteGoal, reorderGoals, submitReview } from '../api/goals'
import * as client from '../api/client'
import { GoalType } from '../types'

// Mock the client module
vi.mock('../api/client', () => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  del: vi.fn(),
}))

describe('Goals API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchGoals', () => {
    it('should fetch goals for a review', async () => {
      const mockGoals = [
        { id: '1', title: 'Goal 1', weight: 50 },
        { id: '2', title: 'Goal 2', weight: 50 },
      ]
      vi.mocked(client.get).mockResolvedValueOnce(mockGoals)

      const result = await fetchGoals('review-123')

      expect(client.get).toHaveBeenCalledWith('/reviews/review-123/goals')
      expect(result).toEqual(mockGoals)
    })
  })

  describe('createGoal', () => {
    it('should create a new goal', async () => {
      const newGoal = {
        id: '1',
        review_id: 'review-123',
        title: 'New Goal',
        goal_type: GoalType.STANDARD,
        weight: 25,
      }
      vi.mocked(client.post).mockResolvedValueOnce(newGoal)

      const result = await createGoal('review-123', {
        title: 'New Goal',
        weight: 25,
      })

      expect(client.post).toHaveBeenCalledWith('/reviews/review-123/goals', {
        title: 'New Goal',
        weight: 25,
      })
      expect(result).toEqual(newGoal)
    })
  })

  describe('updateGoal', () => {
    it('should update an existing goal', async () => {
      const updatedGoal = {
        id: 'goal-1',
        title: 'Updated Title',
        weight: 30,
      }
      vi.mocked(client.put).mockResolvedValueOnce(updatedGoal)

      const result = await updateGoal('goal-1', { title: 'Updated Title' })

      expect(client.put).toHaveBeenCalledWith('/goals/goal-1', { title: 'Updated Title' })
      expect(result).toEqual(updatedGoal)
    })
  })

  describe('deleteGoal', () => {
    it('should delete a goal', async () => {
      vi.mocked(client.del).mockResolvedValueOnce(undefined)

      await deleteGoal('goal-1')

      expect(client.del).toHaveBeenCalledWith('/goals/goal-1')
    })
  })

  describe('reorderGoals', () => {
    it('should reorder goals', async () => {
      vi.mocked(client.put).mockResolvedValueOnce(undefined)

      const goalIds = ['goal-2', 'goal-1', 'goal-3']
      await reorderGoals('review-123', goalIds)

      expect(client.put).toHaveBeenCalledWith('/reviews/review-123/goals/order', {
        goal_ids: goalIds,
      })
    })
  })

  describe('submitReview', () => {
    it('should submit a review', async () => {
      vi.mocked(client.post).mockResolvedValueOnce(undefined)

      await submitReview('review-123')

      expect(client.post).toHaveBeenCalledWith('/reviews/review-123/submit')
    })
  })
})
