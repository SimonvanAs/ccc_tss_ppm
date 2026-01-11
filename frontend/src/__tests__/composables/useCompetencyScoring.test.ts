// TSS PPM v3.0 - useCompetencyScoring Composable Tests
import { describe, it, expect, beforeEach } from 'vitest'
import { useCompetencyScoring } from '../../composables/useCompetencyScoring'

describe('useCompetencyScoring', () => {
  describe('initial state', () => {
    it('should initialize with empty scores map', () => {
      const { scores } = useCompetencyScoring()
      expect(scores.value.size).toBe(0)
    })

    it('should initialize with null HOW score', () => {
      const { howScore } = useCompetencyScoring()
      expect(howScore.value).toBeNull()
    })

    it('should initialize with vetoActive as false', () => {
      const { vetoActive } = useCompetencyScoring()
      expect(vetoActive.value).toBe(false)
    })

    it('should initialize with gridPosition as null', () => {
      const { gridPosition } = useCompetencyScoring()
      expect(gridPosition.value).toBeNull()
    })

    it('should initialize with isComplete as false', () => {
      const { isComplete } = useCompetencyScoring()
      expect(isComplete.value).toBe(false)
    })

    it('should initialize with scoredCount as 0', () => {
      const { scoredCount } = useCompetencyScoring()
      expect(scoredCount.value).toBe(0)
    })
  })

  describe('setScore', () => {
    it('should set a score for a competency', () => {
      const { scores, setScore } = useCompetencyScoring()

      setScore('comp-1', 2)

      expect(scores.value.get('comp-1')).toBe(2)
    })

    it('should update scoredCount when score is set', () => {
      const { scoredCount, setScore } = useCompetencyScoring()

      setScore('comp-1', 2)
      expect(scoredCount.value).toBe(1)

      setScore('comp-2', 3)
      expect(scoredCount.value).toBe(2)
    })

    it('should not increment count when updating existing score', () => {
      const { scoredCount, setScore } = useCompetencyScoring()

      setScore('comp-1', 2)
      expect(scoredCount.value).toBe(1)

      setScore('comp-1', 3)
      expect(scoredCount.value).toBe(1)
    })
  })

  describe('HOW score calculation', () => {
    it('should calculate HOW score when all 6 scores are set', () => {
      const { howScore, setScore } = useCompetencyScoring()

      // Set all 6 scores to 2 -> average = 2.00
      for (let i = 1; i <= 6; i++) {
        setScore(`comp-${i}`, 2)
      }

      expect(howScore.value).toBe(2)
    })

    it('should calculate correct average with mixed scores', () => {
      const { howScore, setScore } = useCompetencyScoring()

      // 3+3+2+2+2+2 = 14 / 6 = 2.33
      setScore('comp-1', 3)
      setScore('comp-2', 3)
      setScore('comp-3', 2)
      setScore('comp-4', 2)
      setScore('comp-5', 2)
      setScore('comp-6', 2)

      expect(howScore.value).toBe(2.33)
    })

    it('should return null when fewer than 6 scores', () => {
      const { howScore, setScore } = useCompetencyScoring()

      setScore('comp-1', 2)
      setScore('comp-2', 2)
      setScore('comp-3', 2)

      expect(howScore.value).toBeNull()
    })

    it('should update score when changed', () => {
      const { howScore, setScore } = useCompetencyScoring()

      // All 2s = 2.00
      for (let i = 1; i <= 6; i++) {
        setScore(`comp-${i}`, 2)
      }
      expect(howScore.value).toBe(2)

      // Change one to 3: (2+2+2+2+2+3) / 6 = 2.17
      setScore('comp-6', 3)
      expect(howScore.value).toBe(2.17)
    })
  })

  describe('VETO detection', () => {
    it('should detect VETO when any score is 1', () => {
      const { vetoActive, setScore } = useCompetencyScoring()

      for (let i = 1; i <= 5; i++) {
        setScore(`comp-${i}`, 2)
      }
      setScore('comp-6', 1) // VETO trigger

      expect(vetoActive.value).toBe(true)
    })

    it('should set HOW score to 1 when VETO is active', () => {
      const { howScore, setScore } = useCompetencyScoring()

      for (let i = 1; i <= 5; i++) {
        setScore(`comp-${i}`, 3)
      }
      setScore('comp-6', 1) // VETO trigger

      expect(howScore.value).toBe(1)
    })

    it('should not trigger VETO when all scores are 2 or 3', () => {
      const { vetoActive, setScore } = useCompetencyScoring()

      for (let i = 1; i <= 6; i++) {
        setScore(`comp-${i}`, i % 2 === 0 ? 2 : 3)
      }

      expect(vetoActive.value).toBe(false)
    })

    it('should detect VETO even with incomplete scores', () => {
      const { vetoActive, setScore } = useCompetencyScoring()

      setScore('comp-1', 1) // VETO trigger

      expect(vetoActive.value).toBe(true)
    })

    it('should track which competency triggered VETO', () => {
      const { vetoCompetencyId, setScore } = useCompetencyScoring()

      setScore('comp-1', 2)
      setScore('comp-2', 1) // This triggers VETO

      expect(vetoCompetencyId.value).toBe('comp-2')
    })
  })

  describe('grid position calculation', () => {
    it('should return grid position 1 for score 1.00-1.66', () => {
      const { gridPosition, setScore } = useCompetencyScoring()

      // All 1s = 1.00 -> position 1
      for (let i = 1; i <= 6; i++) {
        setScore(`comp-${i}`, 1)
      }

      expect(gridPosition.value).toBe(1)
    })

    it('should return grid position 2 for score 1.67-2.33', () => {
      const { gridPosition, setScore } = useCompetencyScoring()

      // All 2s = 2.00 -> position 2
      for (let i = 1; i <= 6; i++) {
        setScore(`comp-${i}`, 2)
      }

      expect(gridPosition.value).toBe(2)
    })

    it('should return grid position 3 for score 2.34-3.00', () => {
      const { gridPosition, setScore } = useCompetencyScoring()

      // All 3s = 3.00 -> position 3
      for (let i = 1; i <= 6; i++) {
        setScore(`comp-${i}`, 3)
      }

      expect(gridPosition.value).toBe(3)
    })

    it('should return null when score is incomplete', () => {
      const { gridPosition, setScore } = useCompetencyScoring()

      setScore('comp-1', 2)
      setScore('comp-2', 2)

      expect(gridPosition.value).toBeNull()
    })

    it('should return 1 when VETO is active', () => {
      const { gridPosition, setScore } = useCompetencyScoring()

      for (let i = 1; i <= 5; i++) {
        setScore(`comp-${i}`, 3)
      }
      setScore('comp-6', 1) // VETO -> score becomes 1.00

      expect(gridPosition.value).toBe(1)
    })
  })

  describe('score completion tracking', () => {
    it('should track number of scores set', () => {
      const { scoredCount, setScore } = useCompetencyScoring()

      expect(scoredCount.value).toBe(0)

      setScore('comp-1', 2)
      expect(scoredCount.value).toBe(1)

      setScore('comp-2', 3)
      expect(scoredCount.value).toBe(2)

      setScore('comp-3', 2)
      expect(scoredCount.value).toBe(3)
    })

    it('should set isComplete to true when all 6 scored', () => {
      const { isComplete, setScore } = useCompetencyScoring()

      expect(isComplete.value).toBe(false)

      for (let i = 1; i <= 6; i++) {
        setScore(`comp-${i}`, 2)
      }

      expect(isComplete.value).toBe(true)
    })

    it('should remain incomplete with 5 scores', () => {
      const { isComplete, setScore } = useCompetencyScoring()

      for (let i = 1; i <= 5; i++) {
        setScore(`comp-${i}`, 2)
      }

      expect(isComplete.value).toBe(false)
    })
  })

  describe('initializeScores', () => {
    it('should initialize with existing scores', () => {
      const { scores, initializeScores } = useCompetencyScoring()

      const existingScores = [
        { id: 'comp-1', score: 2 },
        { id: 'comp-2', score: 3 },
      ]

      initializeScores(existingScores)

      expect(scores.value.get('comp-1')).toBe(2)
      expect(scores.value.get('comp-2')).toBe(3)
    })

    it('should calculate HOW score after initialization', () => {
      const { howScore, initializeScores } = useCompetencyScoring()

      const existingScores = [
        { id: 'comp-1', score: 2 },
        { id: 'comp-2', score: 2 },
        { id: 'comp-3', score: 2 },
        { id: 'comp-4', score: 2 },
        { id: 'comp-5', score: 2 },
        { id: 'comp-6', score: 2 },
      ]

      initializeScores(existingScores)

      expect(howScore.value).toBe(2)
    })

    it('should clear previous scores on initialize', () => {
      const { scores, setScore, initializeScores } = useCompetencyScoring()

      setScore('old-comp', 3)

      initializeScores([{ id: 'new-comp', score: 2 }])

      expect(scores.value.has('old-comp')).toBe(false)
      expect(scores.value.has('new-comp')).toBe(true)
    })
  })

  describe('clearScores', () => {
    it('should clear all scores', () => {
      const { scores, setScore, clearScores } = useCompetencyScoring()

      setScore('comp-1', 2)
      setScore('comp-2', 3)

      clearScores()

      expect(scores.value.size).toBe(0)
    })

    it('should reset computed values after clear', () => {
      const { howScore, scoredCount, isComplete, setScore, clearScores } = useCompetencyScoring()

      for (let i = 1; i <= 6; i++) {
        setScore(`comp-${i}`, 2)
      }

      expect(howScore.value).toBe(2)
      expect(isComplete.value).toBe(true)

      clearScores()

      expect(howScore.value).toBeNull()
      expect(scoredCount.value).toBe(0)
      expect(isComplete.value).toBe(false)
    })
  })

  describe('getScoresArray', () => {
    it('should return scores as array for API submission', () => {
      const { setScore, getScoresArray } = useCompetencyScoring()

      setScore('comp-1', 2)
      setScore('comp-2', 3)

      const scoresArray = getScoresArray()

      expect(scoresArray).toHaveLength(2)
      expect(scoresArray).toContainEqual({ competency_id: 'comp-1', score: 2 })
      expect(scoresArray).toContainEqual({ competency_id: 'comp-2', score: 3 })
    })
  })
})
