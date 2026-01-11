// TSS PPM v3.0 - Scoring Service Tests
import { describe, it, expect } from 'vitest'
import {
  calculateWhatScore,
  calculateHowScore,
  checkScfVeto,
  checkKarVeto,
  checkCompetencyVeto,
  type GoalScore,
  type CompetencyScore,
} from '../../services/scoring'

describe('Scoring Service', () => {
  describe('calculateWhatScore', () => {
    it('should calculate weighted average of goal scores', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 3, weight: 50, goalType: 'STANDARD' },
        { id: '2', score: 2, weight: 50, goalType: 'STANDARD' },
      ]

      const result = calculateWhatScore(goals)

      // (3 * 50 + 2 * 50) / 100 = 2.50
      expect(result.score).toBe(2.5)
      expect(result.vetoActive).toBe(false)
    })

    it('should handle different weights', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 3, weight: 70, goalType: 'STANDARD' },
        { id: '2', score: 1, weight: 30, goalType: 'STANDARD' },
      ]

      const result = calculateWhatScore(goals)

      // (3 * 70 + 1 * 30) / 100 = 2.40
      expect(result.score).toBe(2.4)
    })

    it('should return 0 for empty goals', () => {
      const result = calculateWhatScore([])

      expect(result.score).toBe(0)
    })

    it('should handle single goal', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 2, weight: 100, goalType: 'STANDARD' },
      ]

      const result = calculateWhatScore(goals)

      expect(result.score).toBe(2)
    })

    it('should round to 2 decimal places', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 3, weight: 33, goalType: 'STANDARD' },
        { id: '2', score: 2, weight: 33, goalType: 'STANDARD' },
        { id: '3', score: 1, weight: 34, goalType: 'STANDARD' },
      ]

      const result = calculateWhatScore(goals)

      // (3*33 + 2*33 + 1*34) / 100 = 1.99
      expect(result.score).toBe(1.99)
    })
  })

  describe('SCF VETO Rule', () => {
    it('should trigger VETO when SCF goal scores 1', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 3, weight: 50, goalType: 'STANDARD' },
        { id: '2', score: 1, weight: 50, goalType: 'SCF' },
      ]

      const result = calculateWhatScore(goals)

      expect(result.score).toBe(1)
      expect(result.vetoActive).toBe(true)
      expect(result.vetoReason).toBe('SCF')
    })

    it('should NOT trigger VETO when SCF goal scores 2 or 3', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 3, weight: 50, goalType: 'STANDARD' },
        { id: '2', score: 2, weight: 50, goalType: 'SCF' },
      ]

      const result = calculateWhatScore(goals)

      expect(result.vetoActive).toBe(false)
      expect(result.score).toBe(2.5)
    })

    it('should check SCF veto independently', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 1, weight: 50, goalType: 'SCF' },
      ]

      const vetoResult = checkScfVeto(goals)

      expect(vetoResult.active).toBe(true)
      expect(vetoResult.goalId).toBe('1')
    })
  })

  describe('KAR VETO Rule', () => {
    it('should trigger VETO when KAR goal scores 1 without compensation', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 3, weight: 50, goalType: 'STANDARD' },
        { id: '2', score: 1, weight: 50, goalType: 'KAR' },
      ]

      const result = calculateWhatScore(goals)

      expect(result.score).toBe(1)
      expect(result.vetoActive).toBe(true)
      expect(result.vetoReason).toBe('KAR')
    })

    it('should NOT trigger VETO when KAR=1 is compensated by another KAR=3', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 1, weight: 30, goalType: 'KAR' },
        { id: '2', score: 3, weight: 30, goalType: 'KAR' },
        { id: '3', score: 2, weight: 40, goalType: 'STANDARD' },
      ]

      const result = calculateWhatScore(goals)

      // No VETO because KAR=1 is compensated by KAR=3
      expect(result.vetoActive).toBe(false)
      // (1*30 + 3*30 + 2*40) / 100 = 2.00
      expect(result.score).toBe(2)
    })

    it('should trigger VETO when multiple KAR=1 with only one KAR=3', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 1, weight: 25, goalType: 'KAR' },
        { id: '2', score: 1, weight: 25, goalType: 'KAR' },
        { id: '3', score: 3, weight: 50, goalType: 'KAR' },
      ]

      const result = calculateWhatScore(goals)

      // Two KAR=1 but only one KAR=3, so only one is compensated
      expect(result.vetoActive).toBe(true)
      expect(result.vetoReason).toBe('KAR')
    })

    it('should check KAR veto independently with compensation info', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 1, weight: 50, goalType: 'KAR' },
        { id: '2', score: 3, weight: 50, goalType: 'KAR' },
      ]

      const vetoResult = checkKarVeto(goals)

      expect(vetoResult.active).toBe(false)
      expect(vetoResult.compensated).toBe(true)
      expect(vetoResult.compensatingGoalId).toBe('2')
    })

    it('should report uncompensated KAR veto', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 1, weight: 50, goalType: 'KAR' },
        { id: '2', score: 2, weight: 50, goalType: 'KAR' },
      ]

      const vetoResult = checkKarVeto(goals)

      expect(vetoResult.active).toBe(true)
      expect(vetoResult.compensated).toBe(false)
      expect(vetoResult.goalId).toBe('1')
    })
  })

  describe('calculateHowScore', () => {
    it('should calculate average of competency scores', () => {
      const competencies: CompetencyScore[] = [
        { id: '1', score: 3 },
        { id: '2', score: 2 },
        { id: '3', score: 3 },
        { id: '4', score: 2 },
        { id: '5', score: 3 },
        { id: '6', score: 2 },
      ]

      const result = calculateHowScore(competencies)

      // (3+2+3+2+3+2) / 6 = 2.50
      expect(result.score).toBe(2.5)
      expect(result.vetoActive).toBe(false)
    })

    it('should return 0 for empty competencies', () => {
      const result = calculateHowScore([])

      expect(result.score).toBe(0)
    })

    it('should round to 2 decimal places', () => {
      const competencies: CompetencyScore[] = [
        { id: '1', score: 3 },
        { id: '2', score: 3 },
        { id: '3', score: 2 },
        { id: '4', score: 2 },
        { id: '5', score: 2 },
        { id: '6', score: 2 },
      ]

      const result = calculateHowScore(competencies)

      // (3+3+2+2+2+2) / 6 = 2.333...
      expect(result.score).toBe(2.33)
    })
  })

  describe('Competency VETO Rule', () => {
    it('should trigger VETO when any competency scores 1', () => {
      const competencies: CompetencyScore[] = [
        { id: '1', score: 3 },
        { id: '2', score: 2 },
        { id: '3', score: 1 },
        { id: '4', score: 3 },
        { id: '5', score: 2 },
        { id: '6', score: 3 },
      ]

      const result = calculateHowScore(competencies)

      expect(result.score).toBe(1)
      expect(result.vetoActive).toBe(true)
      expect(result.vetoReason).toBe('COMPETENCY')
    })

    it('should NOT trigger VETO when all competencies score 2 or 3', () => {
      const competencies: CompetencyScore[] = [
        { id: '1', score: 2 },
        { id: '2', score: 2 },
        { id: '3', score: 2 },
        { id: '4', score: 3 },
        { id: '5', score: 3 },
        { id: '6', score: 3 },
      ]

      const result = calculateHowScore(competencies)

      expect(result.vetoActive).toBe(false)
    })

    it('should check competency veto independently', () => {
      const competencies: CompetencyScore[] = [
        { id: '1', score: 1 },
        { id: '2', score: 2 },
      ]

      const vetoResult = checkCompetencyVeto(competencies)

      expect(vetoResult.active).toBe(true)
      expect(vetoResult.competencyId).toBe('1')
    })
  })

  describe('VETO Priority', () => {
    it('SCF VETO should take priority over KAR VETO', () => {
      const goals: GoalScore[] = [
        { id: '1', score: 1, weight: 50, goalType: 'SCF' },
        { id: '2', score: 1, weight: 50, goalType: 'KAR' },
      ]

      const result = calculateWhatScore(goals)

      expect(result.vetoActive).toBe(true)
      expect(result.vetoReason).toBe('SCF')
    })
  })
})
