// TSS PPM v3.0 - Goals Composable
import { ref, computed } from 'vue'
import type { Goal, GoalCreate, GoalUpdate } from '../types'
import { fetchGoals, createGoal, updateGoal, deleteGoal, reorderGoals } from '../api/goals'

export function useGoals(reviewId: string) {
  const goals = ref<Goal[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Calculate total weight of all goals.
   */
  const totalWeight = computed(() => {
    return goals.value.reduce((sum, goal) => sum + goal.weight, 0)
  })

  /**
   * Check if weights are valid (total 100%).
   */
  const isWeightValid = computed(() => totalWeight.value === 100)

  /**
   * Check if maximum goals (9) reached.
   */
  const isMaxGoalsReached = computed(() => goals.value.length >= 9)

  /**
   * Load goals from API.
   */
  async function loadGoals() {
    loading.value = true
    error.value = null
    try {
      goals.value = await fetchGoals(reviewId)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load goals'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Add a new goal.
   */
  async function addGoal(data: GoalCreate) {
    error.value = null
    try {
      const newGoal = await createGoal(reviewId, data)
      goals.value.push(newGoal)
      return newGoal
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create goal'
      throw e
    }
  }

  /**
   * Update an existing goal.
   */
  async function editGoal(goalId: string, data: GoalUpdate) {
    error.value = null
    try {
      const updatedGoal = await updateGoal(goalId, data)
      const index = goals.value.findIndex(g => g.id === goalId)
      if (index !== -1) {
        goals.value[index] = updatedGoal
      }
      return updatedGoal
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update goal'
      throw e
    }
  }

  /**
   * Remove a goal.
   */
  async function removeGoal(goalId: string) {
    error.value = null
    try {
      await deleteGoal(goalId)
      goals.value = goals.value.filter(g => g.id !== goalId)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete goal'
      throw e
    }
  }

  /**
   * Reorder goals.
   */
  async function setGoalOrder(goalIds: string[]) {
    error.value = null
    // Optimistically update local state
    const orderedGoals = goalIds
      .map(id => goals.value.find(g => g.id === id))
      .filter((g): g is Goal => g !== undefined)
      .map((g, i) => ({ ...g, display_order: i }))

    goals.value = orderedGoals

    try {
      await reorderGoals(reviewId, goalIds)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to reorder goals'
      // Reload on error to restore correct order
      await loadGoals()
      throw e
    }
  }

  return {
    goals,
    loading,
    error,
    totalWeight,
    isWeightValid,
    isMaxGoalsReached,
    loadGoals,
    addGoal,
    editGoal,
    removeGoal,
    setGoalOrder,
  }
}
