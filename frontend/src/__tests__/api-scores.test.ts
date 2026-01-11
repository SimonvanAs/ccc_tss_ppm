// TSS PPM v3.0 - Scores API Client Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchScores, saveScores, submitScores } from '../api/scores'
import * as client from '../api/client'

vi.mock('../api/client', () => ({
  get: vi.fn(),
  put: vi.fn(),
  post: vi.fn(),
}))

describe('Scores API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchScores', () => {
    it('should fetch scores for a review', async () => {
      const mockScores = {
        goal_scores: [
          { goal_id: 'goal-1', score: 2, feedback: 'Good progress' },
          { goal_id: 'goal-2', score: 3, feedback: 'Excellent' },
        ],
        competency_scores: [
          { competency_id: 'comp-1', score: 2 },
          { competency_id: 'comp-2', score: 3 },
        ],
      }
      vi.mocked(client.get).mockResolvedValue(mockScores)

      const result = await fetchScores('review-123')

      expect(client.get).toHaveBeenCalledWith('/reviews/review-123/scores')
      expect(result).toEqual(mockScores)
    })

    it('should return empty scores when none exist', async () => {
      const mockScores = {
        goal_scores: [],
        competency_scores: [],
      }
      vi.mocked(client.get).mockResolvedValue(mockScores)

      const result = await fetchScores('review-123')

      expect(result.goal_scores).toEqual([])
      expect(result.competency_scores).toEqual([])
    })

    it('should throw error on fetch failure', async () => {
      vi.mocked(client.get).mockRejectedValue(new Error('Network error'))

      await expect(fetchScores('review-123')).rejects.toThrow('Network error')
    })
  })

  describe('saveScores', () => {
    it('should save goal scores', async () => {
      const scores = {
        goal_scores: [
          { goal_id: 'goal-1', score: 2, feedback: 'Updated feedback' },
        ],
        competency_scores: [],
      }
      vi.mocked(client.put).mockResolvedValue(scores)

      const result = await saveScores('review-123', scores)

      expect(client.put).toHaveBeenCalledWith('/reviews/review-123/scores', scores)
      expect(result).toEqual(scores)
    })

    it('should save competency scores', async () => {
      const scores = {
        goal_scores: [],
        competency_scores: [
          { competency_id: 'comp-1', score: 3 },
        ],
      }
      vi.mocked(client.put).mockResolvedValue(scores)

      const result = await saveScores('review-123', scores)

      expect(client.put).toHaveBeenCalledWith('/reviews/review-123/scores', scores)
      expect(result).toEqual(scores)
    })

    it('should save both goal and competency scores', async () => {
      const scores = {
        goal_scores: [
          { goal_id: 'goal-1', score: 2, feedback: 'Good' },
        ],
        competency_scores: [
          { competency_id: 'comp-1', score: 3 },
        ],
      }
      vi.mocked(client.put).mockResolvedValue(scores)

      await saveScores('review-123', scores)

      expect(client.put).toHaveBeenCalledWith('/reviews/review-123/scores', scores)
    })

    it('should throw error on save failure', async () => {
      vi.mocked(client.put).mockRejectedValue(new Error('Save failed'))

      await expect(saveScores('review-123', { goal_scores: [], competency_scores: [] }))
        .rejects.toThrow('Save failed')
    })
  })

  describe('submitScores', () => {
    it('should submit scores for a review', async () => {
      const mockResponse = { status: 'PENDING_EMPLOYEE_SIGNATURE' }
      vi.mocked(client.post).mockResolvedValue(mockResponse)

      const result = await submitScores('review-123')

      expect(client.post).toHaveBeenCalledWith('/reviews/review-123/submit-scores', {})
      expect(result).toEqual(mockResponse)
    })

    it('should throw error when scores are incomplete', async () => {
      vi.mocked(client.post).mockRejectedValue(new Error('All scores must be entered before submission'))

      await expect(submitScores('review-123'))
        .rejects.toThrow('All scores must be entered before submission')
    })

    it('should throw error on submit failure', async () => {
      vi.mocked(client.post).mockRejectedValue(new Error('Submission failed'))

      await expect(submitScores('review-123'))
        .rejects.toThrow('Submission failed')
    })
  })
})
