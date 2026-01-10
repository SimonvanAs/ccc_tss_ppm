// TSS PPM v3.0 - useGoals Composable Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { nextTick } from 'vue'
import { useGoals } from '../../composables/useGoals'
import * as goalsApi from '../../api/goals'
import { GoalType } from '../../types'
import type { Goal, GoalCreate, GoalUpdate } from '../../types'

// Mock the goals API module
vi.mock('../../api/goals', () => ({
  fetchGoals: vi.fn(),
  createGoal: vi.fn(),
  updateGoal: vi.fn(),
  deleteGoal: vi.fn(),
  reorderGoals: vi.fn(),
}))

describe('useGoals', () => {
  const reviewId = 'review-123'

  // Create fresh mock data for each test
  function createMockGoals(): Goal[] {
    return [
      {
        id: 'goal-1',
        review_id: reviewId,
        title: 'Goal 1',
        description: 'Description 1',
        goal_type: GoalType.STANDARD,
        weight: 30,
        score: null,
        display_order: 0,
      },
      {
        id: 'goal-2',
        review_id: reviewId,
        title: 'Goal 2',
        description: null,
        goal_type: GoalType.KAR,
        weight: 40,
        score: null,
        display_order: 1,
      },
      {
        id: 'goal-3',
        review_id: reviewId,
        title: 'Goal 3',
        description: 'Description 3',
        goal_type: GoalType.SCF,
        weight: 30,
        score: null,
        display_order: 2,
      },
    ]
  }

  beforeEach(() => {
    vi.resetAllMocks()
  })

  describe('initial state', () => {
    it('should initialize with empty goals array', () => {
      const { goals } = useGoals(reviewId)
      expect(goals.value).toEqual([])
    })

    it('should initialize with loading false', () => {
      const { loading } = useGoals(reviewId)
      expect(loading.value).toBe(false)
    })

    it('should initialize with error null', () => {
      const { error } = useGoals(reviewId)
      expect(error.value).toBeNull()
    })

    it('should have totalWeight computed as 0 initially', () => {
      const { totalWeight } = useGoals(reviewId)
      expect(totalWeight.value).toBe(0)
    })

    it('should have isWeightValid false when empty', () => {
      const { isWeightValid } = useGoals(reviewId)
      expect(isWeightValid.value).toBe(false)
    })

    it('should have isMaxGoalsReached false when empty', () => {
      const { isMaxGoalsReached } = useGoals(reviewId)
      expect(isMaxGoalsReached.value).toBe(false)
    })
  })

  describe('loadGoals', () => {
    it('should fetch goals from API', async () => {
      const mockGoals = createMockGoals()
      vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)

      const { goals, loadGoals } = useGoals(reviewId)
      await loadGoals()

      expect(goalsApi.fetchGoals).toHaveBeenCalledWith(reviewId)
      expect(goals.value).toEqual(mockGoals)
    })

    it('should set loading to true while fetching', async () => {
      const mockGoals = createMockGoals()
      let resolvePromise: (value: Goal[]) => void
      vi.mocked(goalsApi.fetchGoals).mockReturnValueOnce(
        new Promise(resolve => {
          resolvePromise = resolve
        })
      )

      const { loading, loadGoals } = useGoals(reviewId)
      const loadPromise = loadGoals()

      expect(loading.value).toBe(true)

      resolvePromise!(mockGoals)
      await loadPromise

      expect(loading.value).toBe(false)
    })

    it('should set error on failure', async () => {
      const errorMessage = 'Network error'
      vi.mocked(goalsApi.fetchGoals).mockRejectedValueOnce(new Error(errorMessage))

      const { error, loadGoals } = useGoals(reviewId)

      await expect(loadGoals()).rejects.toThrow()
      expect(error.value).toBe(errorMessage)
    })

    it('should clear error before fetching', async () => {
      const mockGoals = createMockGoals()
      vi.mocked(goalsApi.fetchGoals)
        .mockRejectedValueOnce(new Error('First error'))
        .mockResolvedValueOnce(mockGoals)

      const { error, loadGoals } = useGoals(reviewId)

      await expect(loadGoals()).rejects.toThrow()
      expect(error.value).toBe('First error')

      await loadGoals()
      expect(error.value).toBeNull()
    })
  })

  describe('addGoal', () => {
    const newGoalData: GoalCreate = {
      title: 'New Goal',
      description: 'New description',
      goal_type: GoalType.STANDARD,
      weight: 25,
    }

    const newGoal: Goal = {
      id: 'goal-new',
      review_id: reviewId,
      ...newGoalData,
      score: null,
      display_order: 0,
    }

    it('should create goal via API', async () => {
      vi.mocked(goalsApi.createGoal).mockResolvedValueOnce(newGoal)

      const { addGoal } = useGoals(reviewId)
      await addGoal(newGoalData)

      expect(goalsApi.createGoal).toHaveBeenCalledWith(reviewId, newGoalData)
    })

    it('should add goal to local state', async () => {
      vi.mocked(goalsApi.createGoal).mockResolvedValueOnce(newGoal)

      const { goals, addGoal } = useGoals(reviewId)
      await addGoal(newGoalData)

      expect(goals.value).toContainEqual(newGoal)
    })

    it('should return the created goal', async () => {
      vi.mocked(goalsApi.createGoal).mockResolvedValueOnce(newGoal)

      const { addGoal } = useGoals(reviewId)
      const result = await addGoal(newGoalData)

      expect(result).toEqual(newGoal)
    })

    it('should set error on failure', async () => {
      vi.mocked(goalsApi.createGoal).mockRejectedValueOnce(new Error('Create failed'))

      const { error, addGoal } = useGoals(reviewId)

      await expect(addGoal(newGoalData)).rejects.toThrow()
      expect(error.value).toBe('Create failed')
    })
  })

  describe('editGoal', () => {
    const updates: GoalUpdate = {
      title: 'Updated Title',
      weight: 35,
    }

    it('should update goal via API', async () => {
      const mockGoals = createMockGoals()
      vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)
      vi.mocked(goalsApi.updateGoal).mockResolvedValueOnce({
        ...mockGoals[0],
        ...updates,
      })

      const { loadGoals, editGoal } = useGoals(reviewId)
      await loadGoals()
      await editGoal('goal-1', updates)

      expect(goalsApi.updateGoal).toHaveBeenCalledWith('goal-1', updates)
    })

    it('should update goal in local state', async () => {
      const mockGoals = createMockGoals()
      vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)
      vi.mocked(goalsApi.updateGoal).mockResolvedValueOnce({
        ...mockGoals[0],
        ...updates,
      })

      const { goals, loadGoals, editGoal } = useGoals(reviewId)
      await loadGoals()
      await editGoal('goal-1', updates)

      const updatedGoal = goals.value.find(g => g.id === 'goal-1')
      expect(updatedGoal?.title).toBe('Updated Title')
      expect(updatedGoal?.weight).toBe(35)
    })

    it('should return the updated goal', async () => {
      const mockGoals = createMockGoals()
      vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)
      const expectedUpdated = { ...mockGoals[0], ...updates }
      vi.mocked(goalsApi.updateGoal).mockResolvedValueOnce(expectedUpdated)

      const { loadGoals, editGoal } = useGoals(reviewId)
      await loadGoals()
      const result = await editGoal('goal-1', updates)

      expect(result).toEqual(expectedUpdated)
    })

    it('should set error on failure', async () => {
      const mockGoals = createMockGoals()
      vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)
      vi.mocked(goalsApi.updateGoal).mockRejectedValueOnce(new Error('Update failed'))

      const { error, loadGoals, editGoal } = useGoals(reviewId)
      await loadGoals()

      await expect(editGoal('goal-1', updates)).rejects.toThrow()
      expect(error.value).toBe('Update failed')
    })
  })

  describe('removeGoal', () => {
    it('should delete goal via API', async () => {
      const mockGoals = createMockGoals()
      vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)
      vi.mocked(goalsApi.deleteGoal).mockResolvedValueOnce(undefined)

      const { loadGoals, removeGoal } = useGoals(reviewId)
      await loadGoals()
      await removeGoal('goal-1')

      expect(goalsApi.deleteGoal).toHaveBeenCalledWith('goal-1')
    })

    it('should remove goal from local state', async () => {
      const mockGoals = createMockGoals()
      vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)
      vi.mocked(goalsApi.deleteGoal).mockResolvedValueOnce(undefined)

      const { goals, loadGoals, removeGoal } = useGoals(reviewId)
      await loadGoals()
      await removeGoal('goal-1')

      expect(goals.value.find(g => g.id === 'goal-1')).toBeUndefined()
      expect(goals.value).toHaveLength(2)
    })

    it('should set error on failure', async () => {
      const mockGoals = createMockGoals()
      vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)
      vi.mocked(goalsApi.deleteGoal).mockRejectedValueOnce(new Error('Delete failed'))

      const { error, loadGoals, removeGoal } = useGoals(reviewId)
      await loadGoals()

      await expect(removeGoal('goal-1')).rejects.toThrow()
      expect(error.value).toBe('Delete failed')
    })
  })

  describe('setGoalOrder', () => {
    it('should reorder goals via API', async () => {
      const mockGoals = createMockGoals()
      vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)
      vi.mocked(goalsApi.reorderGoals).mockResolvedValueOnce(undefined)

      const { loadGoals, setGoalOrder } = useGoals(reviewId)
      await loadGoals()

      const newOrder = ['goal-3', 'goal-1', 'goal-2']
      await setGoalOrder(newOrder)

      expect(goalsApi.reorderGoals).toHaveBeenCalledWith(reviewId, newOrder)
    })

    it('should update local state optimistically', async () => {
      const mockGoals = createMockGoals()
      vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)
      vi.mocked(goalsApi.reorderGoals).mockResolvedValueOnce(undefined)

      const { goals, loadGoals, setGoalOrder } = useGoals(reviewId)
      await loadGoals()

      const newOrder = ['goal-3', 'goal-1', 'goal-2']
      await setGoalOrder(newOrder)

      expect(goals.value[0].id).toBe('goal-3')
      expect(goals.value[1].id).toBe('goal-1')
      expect(goals.value[2].id).toBe('goal-2')
    })

    it('should reload goals on API failure', async () => {
      const mockGoals = createMockGoals()
      vi.mocked(goalsApi.fetchGoals)
        .mockResolvedValueOnce(mockGoals)
        .mockResolvedValueOnce(mockGoals) // Called again after error
      vi.mocked(goalsApi.reorderGoals).mockRejectedValueOnce(new Error('Reorder failed'))

      const { error, loadGoals, setGoalOrder } = useGoals(reviewId)
      await loadGoals()

      await expect(setGoalOrder(['goal-3', 'goal-1', 'goal-2'])).rejects.toThrow()

      // After reload, error gets cleared, so check that reload was called
      expect(goalsApi.fetchGoals).toHaveBeenCalledTimes(2)
    })
  })

  describe('computed properties', () => {
    describe('totalWeight', () => {
      it('should calculate sum of all goal weights', async () => {
        const mockGoals = createMockGoals()
        vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)

        const { totalWeight, loadGoals } = useGoals(reviewId)
        await loadGoals()

        expect(totalWeight.value).toBe(100) // 30 + 40 + 30
      })

      it('should update when goal is added', async () => {
        const mockGoals = createMockGoals()
        vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce([mockGoals[0]])
        vi.mocked(goalsApi.createGoal).mockResolvedValueOnce(mockGoals[1])

        const { totalWeight, loadGoals, addGoal } = useGoals(reviewId)
        await loadGoals()
        expect(totalWeight.value).toBe(30)

        await addGoal({ title: 'New', weight: 40 })
        expect(totalWeight.value).toBe(70)
      })

      it('should update when goal is removed', async () => {
        const mockGoals = createMockGoals()
        vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)
        vi.mocked(goalsApi.deleteGoal).mockResolvedValueOnce(undefined)

        const { totalWeight, loadGoals, removeGoal } = useGoals(reviewId)
        await loadGoals()
        expect(totalWeight.value).toBe(100)

        await removeGoal('goal-1')
        expect(totalWeight.value).toBe(70)
      })
    })

    describe('isWeightValid', () => {
      it('should be true when total is exactly 100', async () => {
        const mockGoals = createMockGoals()
        vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)

        const { isWeightValid, loadGoals } = useGoals(reviewId)
        await loadGoals()

        expect(isWeightValid.value).toBe(true)
      })

      it('should be false when total is less than 100', async () => {
        const mockGoals = createMockGoals()
        vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce([mockGoals[0]])

        const { isWeightValid, loadGoals } = useGoals(reviewId)
        await loadGoals()

        expect(isWeightValid.value).toBe(false)
      })

      it('should be false when total is more than 100', async () => {
        const mockGoals = createMockGoals()
        const overweightGoals = [
          { ...mockGoals[0], weight: 60 },
          { ...mockGoals[1], weight: 60 },
        ]
        vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(overweightGoals)

        const { isWeightValid, loadGoals } = useGoals(reviewId)
        await loadGoals()

        expect(isWeightValid.value).toBe(false)
      })
    })

    describe('isMaxGoalsReached', () => {
      it('should be false when goals count is less than 9', async () => {
        const mockGoals = createMockGoals()
        vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(mockGoals)

        const { isMaxGoalsReached, loadGoals } = useGoals(reviewId)
        await loadGoals()

        expect(isMaxGoalsReached.value).toBe(false)
      })

      it('should be true when goals count is 9', async () => {
        const mockGoals = createMockGoals()
        const nineGoals = Array.from({ length: 9 }, (_, i) => ({
          ...mockGoals[0],
          id: `goal-${i}`,
          display_order: i,
        }))
        vi.mocked(goalsApi.fetchGoals).mockResolvedValueOnce(nineGoals)

        const { isMaxGoalsReached, loadGoals } = useGoals(reviewId)
        await loadGoals()

        expect(isMaxGoalsReached.value).toBe(true)
      })
    })
  })
})
