// TSS PPM v3.0 - useScoring Composable
import { ref, computed } from 'vue'
import { fetchScores, saveScores, type ScoresData } from '../api/scores'

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error'

export interface GoalScoreState {
  score: number | null
  feedback?: string
}

export interface CompetencyScoreState {
  score: number | null
}

export function useScoring(reviewId: string) {
  // State
  const goalScores = ref<Record<string, GoalScoreState>>({})
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

    const scoresData: ScoresData = {
      goal_scores: Object.entries(goalScores.value).map(([goalId, data]) => ({
        goal_id: goalId,
        score: data.score,
        feedback: data.feedback,
      })),
      competency_scores: Object.entries(competencyScores.value).map(([compId, data]) => ({
        competency_id: compId,
        score: data.score,
      })),
    }

    try {
      await saveScores(reviewId, scoresData)
      saveStatus.value = 'saved'
    } catch {
      saveStatus.value = 'error'
    }
  }

  async function loadScores() {
    isLoading.value = true
    loadError.value = null

    try {
      const data = await fetchScores(reviewId)

      // Populate goal scores
      for (const gs of data.goal_scores) {
        goalScores.value[gs.goal_id] = {
          score: gs.score,
          feedback: gs.feedback,
        }
      }

      // Populate competency scores
      for (const cs of data.competency_scores) {
        competencyScores.value[cs.competency_id] = {
          score: cs.score,
        }
      }
    } catch (error) {
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
