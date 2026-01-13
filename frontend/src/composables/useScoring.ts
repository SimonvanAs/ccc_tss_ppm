// TSS PPM v3.0 - useScoring Composable
import { ref, computed } from 'vue'
import {
  fetchScores,
  saveScores,
  type ScoresUpdateRequest,
  type GoalScoreUpdate,
  type CompetencyScoreUpdate,
} from '../api/scores'

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error'

export interface GoalScoreState {
  score: number | null
  feedback?: string
}

export interface CompetencyScoreState {
  score: number | null
}

export function useScoring(reviewId: string) {
  // State - keyed by goal ID (from the goals table)
  const goalScores = ref<Record<string, GoalScoreState>>({})
  // State - keyed by competency ID (from the competencies table)
  const competencyScores = ref<Record<string, CompetencyScoreState>>({})
  const requiredGoals = ref<string[]>([])
  const requiredCompetencies = ref<string[]>([])
  const saveStatus = ref<SaveStatus>('idle')
  const isLoading = ref(false)
  const loadError = ref<string | null>(null)

  // Debounce timer
  let debounceTimer: ReturnType<typeof setTimeout> | null = null
  const DEBOUNCE_MS = 500

  // Computed
  const allGoalsScored = computed(() => {
    if (requiredGoals.value.length === 0) return false
    return requiredGoals.value.every((goalId) => {
      const score = goalScores.value[goalId]
      return score && score.score !== null
    })
  })

  const allCompetenciesScored = computed(() => {
    if (requiredCompetencies.value.length === 0) return false
    return requiredCompetencies.value.every((compId) => {
      const score = competencyScores.value[compId]
      return score && score.score !== null
    })
  })

  const allScoresComplete = computed(() => {
    return allGoalsScored.value && allCompetenciesScored.value
  })

  // Actions
  function setRequiredGoals(goalIds: string[]) {
    requiredGoals.value = goalIds
  }

  function setRequiredCompetencies(compIds: string[]) {
    requiredCompetencies.value = compIds
  }

  function setGoalScore(goalId: string, score: number | null, feedback?: string) {
    goalScores.value[goalId] = {
      score,
      feedback: feedback ?? goalScores.value[goalId]?.feedback,
    }
    scheduleSave()
  }

  function setGoalFeedback(goalId: string, feedback: string) {
    console.log('[useScoring] setGoalFeedback called:', { goalId, feedback: feedback.substring(0, 50) })
    if (!goalScores.value[goalId]) {
      goalScores.value[goalId] = { score: null, feedback }
    } else {
      goalScores.value[goalId].feedback = feedback
    }
    scheduleSave()
  }

  function setCompetencyScore(compId: string, score: number | null) {
    competencyScores.value[compId] = { score }
    scheduleSave()
  }

  function scheduleSave() {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    debounceTimer = setTimeout(() => {
      performSave()
    }, DEBOUNCE_MS)
  }

  async function performSave() {
    saveStatus.value = 'saving'

    // Build request with goal_id (for goals) and competency_id (for competencies)
    const request: ScoresUpdateRequest = {
      goal_scores: Object.entries(goalScores.value).map(([goalId, data]): GoalScoreUpdate => ({
        goal_id: goalId,
        score: data.score,
        feedback: data.feedback,
      })),
      competency_scores: Object.entries(competencyScores.value).map(([compId, data]): CompetencyScoreUpdate => ({
        competency_id: compId,
        score: data.score,
      })),
    }

    console.log('[useScoring] performSave - request:', JSON.stringify(request, null, 2))

    try {
      const result = await saveScores(reviewId, request)
      console.log('[useScoring] performSave - success:', result)
      saveStatus.value = 'saved'
    } catch (error) {
      console.error('[useScoring] performSave - error:', error)
      saveStatus.value = 'error'
    }
  }

  async function loadScores() {
    isLoading.value = true
    loadError.value = null

    try {
      const data = await fetchScores(reviewId)
      console.log('[useScoring] loadScores - API response:', JSON.stringify(data, null, 2))

      // Populate goal scores - response uses 'id' (the goal's ID)
      for (const gs of data.goal_scores) {
        goalScores.value[gs.id] = {
          score: gs.score,
          feedback: gs.feedback,
        }
      }

      // Populate competency scores - response uses 'competency_id'
      for (const cs of data.competency_scores) {
        competencyScores.value[cs.competency_id] = {
          score: cs.score,
        }
      }

      console.log('[useScoring] loadScores - populated goalScores:', JSON.stringify(goalScores.value, null, 2))
    } catch (error) {
      console.error('[useScoring] loadScores - error:', error)
      loadError.value = error instanceof Error ? error.message : 'Unknown error'
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    goalScores,
    competencyScores,
    saveStatus,
    isLoading,
    loadError,

    // Computed
    allGoalsScored,
    allCompetenciesScored,
    allScoresComplete,

    // Actions
    setRequiredGoals,
    setRequiredCompetencies,
    setGoalScore,
    setGoalFeedback,
    setCompetencyScore,
    loadScores,
  }
}
