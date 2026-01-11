// TSS PPM v3.0 - useCompetencyScoring Composable
import { ref, computed } from 'vue'
import { calculateHowScore, checkCompetencyVeto, type CompetencyScore } from '../services/scoring'

interface ScoreInput {
  id: string
  score: number
}

interface ScoreOutput {
  competency_id: string
  score: number
}

/**
 * Composable for managing competency scoring with HOW score calculation.
 *
 * Features:
 * - Reactive score state management
 * - HOW score calculation (average of 6 competency scores)
 * - VETO detection (any score = 1 triggers VETO, sets HOW = 1.00)
 * - Grid position calculation for 9-Grid integration
 * - Completion tracking (X/6 scored)
 */
export function useCompetencyScoring() {
  // Reactive state
  const scores = ref<Map<string, number>>(new Map())

  // Computed: number of competencies scored
  const scoredCount = computed(() => scores.value.size)

  // Computed: whether all 6 competencies are scored
  const isComplete = computed(() => scoredCount.value >= 6)

  // Computed: check for VETO (any score = 1)
  const vetoResult = computed(() => {
    if (scores.value.size === 0) {
      return { active: false, competencyId: undefined }
    }

    const competencyScores: CompetencyScore[] = Array.from(scores.value.entries()).map(
      ([id, score]) => ({ id, score })
    )

    return checkCompetencyVeto(competencyScores)
  })

  const vetoActive = computed(() => vetoResult.value.active)
  const vetoCompetencyId = computed(() => vetoResult.value.competencyId)

  // Computed: HOW score (null if incomplete, 1.00 if VETO, otherwise average)
  const howScore = computed((): number | null => {
    if (!isComplete.value) {
      return null
    }

    const competencyScores: CompetencyScore[] = Array.from(scores.value.entries()).map(
      ([id, score]) => ({ id, score })
    )

    const result = calculateHowScore(competencyScores)
    return result.score
  })

  // Computed: grid position (1, 2, or 3) based on HOW score
  const gridPosition = computed((): number | null => {
    if (howScore.value === null) {
      return null
    }

    const score = howScore.value
    if (score <= 1.66) {
      return 1
    } else if (score <= 2.33) {
      return 2
    } else {
      return 3
    }
  })

  /**
   * Set a score for a competency.
   */
  function setScore(competencyId: string, score: number): void {
    scores.value.set(competencyId, score)
    // Trigger reactivity
    scores.value = new Map(scores.value)
  }

  /**
   * Initialize with existing scores (e.g., from API).
   */
  function initializeScores(existingScores: ScoreInput[]): void {
    scores.value = new Map()
    for (const { id, score } of existingScores) {
      scores.value.set(id, score)
    }
    // Trigger reactivity
    scores.value = new Map(scores.value)
  }

  /**
   * Clear all scores.
   */
  function clearScores(): void {
    scores.value = new Map()
  }

  /**
   * Get scores as array for API submission.
   */
  function getScoresArray(): ScoreOutput[] {
    return Array.from(scores.value.entries()).map(([id, score]) => ({
      competency_id: id,
      score,
    }))
  }

  return {
    // State
    scores,

    // Computed
    scoredCount,
    isComplete,
    vetoActive,
    vetoCompetencyId,
    howScore,
    gridPosition,

    // Methods
    setScore,
    initializeScores,
    clearScores,
    getScoresArray,
  }
}
