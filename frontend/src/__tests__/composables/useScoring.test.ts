// TSS PPM v3.0 - useScoring Composable Tests
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { nextTick } from 'vue'
import { useScoring } from '../../composables/useScoring'
import * as scoresApi from '../../api/scores'

vi.mock('../../api/scores', () => ({
  fetchScores: vi.fn(),
  saveScores: vi.fn(),
}))

describe('useScoring', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('score state management', () => {
    it('should initialize with empty scores', () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })

      const { goalScores, competencyScores } = useScoring('review-123')

      expect(goalScores.value).toEqual({})
      expect(competencyScores.value).toEqual({})
    })

    it('should update goal score', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })
      vi.mocked(scoresApi.saveScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })

      const { goalScores, setGoalScore } = useScoring('review-123')

      setGoalScore('goal-1', 2, 'Good progress')
      await nextTick()

      expect(goalScores.value['goal-1']).toEqual({
        score: 2,
        feedback: 'Good progress',
      })
    })

    it('should update competency score', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })
      vi.mocked(scoresApi.saveScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })

      const { competencyScores, setCompetencyScore } = useScoring('review-123')

      setCompetencyScore('comp-1', 3)
      await nextTick()

      expect(competencyScores.value['comp-1']).toEqual({ score: 3 })
    })

    it('should track if all goals are scored', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })
      vi.mocked(scoresApi.saveScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })

      const { allGoalsScored, setGoalScore, setRequiredGoals } = useScoring('review-123')

      setRequiredGoals(['goal-1', 'goal-2'])
      expect(allGoalsScored.value).toBe(false)

      setGoalScore('goal-1', 2)
      await nextTick()
      expect(allGoalsScored.value).toBe(false)

      setGoalScore('goal-2', 3)
      await nextTick()
      expect(allGoalsScored.value).toBe(true)
    })

    it('should track if all competencies are scored', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })
      vi.mocked(scoresApi.saveScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })

      const { allCompetenciesScored, setCompetencyScore, setRequiredCompetencies } = useScoring('review-123')

      setRequiredCompetencies(['comp-1', 'comp-2'])
      expect(allCompetenciesScored.value).toBe(false)

      setCompetencyScore('comp-1', 2)
      await nextTick()
      expect(allCompetenciesScored.value).toBe(false)

      setCompetencyScore('comp-2', 3)
      await nextTick()
      expect(allCompetenciesScored.value).toBe(true)
    })
  })

  describe('auto-save with debounce', () => {
    it('should debounce save calls for 500ms', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })
      vi.mocked(scoresApi.saveScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })

      const { setGoalScore } = useScoring('review-123')

      setGoalScore('goal-1', 1)
      setGoalScore('goal-1', 2)
      setGoalScore('goal-1', 3)

      // Not called yet (debouncing)
      expect(scoresApi.saveScores).not.toHaveBeenCalled()

      // Advance past debounce
      await vi.advanceTimersByTimeAsync(500)

      // Now called once
      expect(scoresApi.saveScores).toHaveBeenCalledTimes(1)
    })

    it('should save with latest score values after debounce', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })
      vi.mocked(scoresApi.saveScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })

      const { setGoalScore } = useScoring('review-123')

      setGoalScore('goal-1', 1)
      setGoalScore('goal-1', 2)
      setGoalScore('goal-1', 3)

      await vi.advanceTimersByTimeAsync(500)

      expect(scoresApi.saveScores).toHaveBeenCalledWith('review-123', expect.objectContaining({
        goal_scores: expect.arrayContaining([
          expect.objectContaining({ goal_id: 'goal-1', score: 3 }),
        ]),
      }))
    })

    it('should reset debounce timer on new changes', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })
      vi.mocked(scoresApi.saveScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })

      const { setGoalScore } = useScoring('review-123')

      setGoalScore('goal-1', 1)
      await vi.advanceTimersByTimeAsync(300)

      setGoalScore('goal-1', 2)
      await vi.advanceTimersByTimeAsync(300)

      // Still not called (timer reset)
      expect(scoresApi.saveScores).not.toHaveBeenCalled()

      await vi.advanceTimersByTimeAsync(200)

      // Now called
      expect(scoresApi.saveScores).toHaveBeenCalledTimes(1)
    })
  })

  describe('save status tracking', () => {
    it('should show "idle" status initially', () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })

      const { saveStatus } = useScoring('review-123')

      expect(saveStatus.value).toBe('idle')
    })

    it('should show "saving" status during save', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })
      let resolvePromise: (value: any) => void
      vi.mocked(scoresApi.saveScores).mockReturnValue(
        new Promise((resolve) => {
          resolvePromise = resolve
        })
      )

      const { saveStatus, setGoalScore } = useScoring('review-123')

      setGoalScore('goal-1', 2)
      await vi.advanceTimersByTimeAsync(500)

      expect(saveStatus.value).toBe('saving')

      resolvePromise!({ goal_scores: [], competency_scores: [] })
      await nextTick()
    })

    it('should show "saved" status after successful save', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })
      vi.mocked(scoresApi.saveScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })

      const { saveStatus, setGoalScore } = useScoring('review-123')

      setGoalScore('goal-1', 2)
      await vi.advanceTimersByTimeAsync(500)
      await nextTick()

      expect(saveStatus.value).toBe('saved')
    })

    it('should show "error" status after failed save', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [],
        competency_scores: [],
      })
      vi.mocked(scoresApi.saveScores).mockRejectedValue(new Error('Save failed'))

      const { saveStatus, setGoalScore } = useScoring('review-123')

      setGoalScore('goal-1', 2)
      await vi.advanceTimersByTimeAsync(500)
      await nextTick()

      expect(saveStatus.value).toBe('error')
    })
  })

  describe('loading existing scores', () => {
    it('should load existing scores on initialization', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [
          { goal_id: 'goal-1', score: 2, feedback: 'Good' },
          { goal_id: 'goal-2', score: 3, feedback: 'Excellent' },
        ],
        competency_scores: [
          { competency_id: 'comp-1', score: 2 },
          { competency_id: 'comp-2', score: 3 },
        ],
      })

      const { goalScores, competencyScores, loadScores } = useScoring('review-123')

      await loadScores()

      expect(goalScores.value['goal-1']).toEqual({ score: 2, feedback: 'Good' })
      expect(goalScores.value['goal-2']).toEqual({ score: 3, feedback: 'Excellent' })
      expect(competencyScores.value['comp-1']).toEqual({ score: 2 })
      expect(competencyScores.value['comp-2']).toEqual({ score: 3 })
    })

    it('should set loading state while fetching', async () => {
      let resolvePromise: (value: any) => void
      vi.mocked(scoresApi.fetchScores).mockReturnValue(
        new Promise((resolve) => {
          resolvePromise = resolve
        })
      )

      const { isLoading, loadScores } = useScoring('review-123')

      const loadPromise = loadScores()
      expect(isLoading.value).toBe(true)

      resolvePromise!({ goal_scores: [], competency_scores: [] })
      await loadPromise

      expect(isLoading.value).toBe(false)
    })

    it('should handle load errors', async () => {
      vi.mocked(scoresApi.fetchScores).mockRejectedValue(new Error('Load failed'))

      const { loadError, loadScores } = useScoring('review-123')

      await loadScores()

      expect(loadError.value).toBe('Load failed')
    })
  })
})
