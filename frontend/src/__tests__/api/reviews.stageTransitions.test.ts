// TSS PPM v3.0 - Stage Transition API Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { advanceReviewStage, bulkAdvanceStage, getStageName, getNextStage } from '../../api/reviews'
import type { ReviewStage } from '../../api/reviews'

// Mock the API client
vi.mock('../../api/client', () => ({
  post: vi.fn(),
}))

import { post } from '../../api/client'

describe('Stage Transition API', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  describe('advanceReviewStage', () => {
    it('should call POST /reviews/:id/advance-stage', async () => {
      const mockResponse = {
        id: 'review-123',
        old_stage: 'GOAL_SETTING',
        new_stage: 'MID_YEAR_REVIEW',
        status: 'DRAFT',
      }
      vi.mocked(post).mockResolvedValue(mockResponse)

      const result = await advanceReviewStage('review-123')

      expect(post).toHaveBeenCalledWith('/reviews/review-123/advance-stage', {})
      expect(result).toEqual(mockResponse)
    })

    it('should return stage transition response', async () => {
      const mockResponse = {
        id: 'review-456',
        old_stage: 'MID_YEAR_REVIEW',
        new_stage: 'END_YEAR_REVIEW',
        status: 'DRAFT',
      }
      vi.mocked(post).mockResolvedValue(mockResponse)

      const result = await advanceReviewStage('review-456')

      expect(result.old_stage).toBe('MID_YEAR_REVIEW')
      expect(result.new_stage).toBe('END_YEAR_REVIEW')
    })
  })

  describe('bulkAdvanceStage', () => {
    it('should call POST /hr/reviews/advance-stage with from_stage', async () => {
      const mockResponse = {
        advanced_count: 5,
        from_stage: 'GOAL_SETTING',
        to_stage: 'MID_YEAR_REVIEW',
      }
      vi.mocked(post).mockResolvedValue(mockResponse)

      const result = await bulkAdvanceStage({
        from_stage: 'GOAL_SETTING',
      })

      expect(post).toHaveBeenCalledWith('/hr/reviews/advance-stage', {
        from_stage: 'GOAL_SETTING',
      })
      expect(result.advanced_count).toBe(5)
    })

    it('should include review_year when provided', async () => {
      const mockResponse = {
        advanced_count: 3,
        from_stage: 'GOAL_SETTING',
        to_stage: 'MID_YEAR_REVIEW',
      }
      vi.mocked(post).mockResolvedValue(mockResponse)

      const result = await bulkAdvanceStage({
        from_stage: 'GOAL_SETTING',
        review_year: 2026,
      })

      expect(post).toHaveBeenCalledWith('/hr/reviews/advance-stage', {
        from_stage: 'GOAL_SETTING',
        review_year: 2026,
      })
      expect(result.advanced_count).toBe(3)
    })

    it('should handle zero reviews to advance', async () => {
      const mockResponse = {
        advanced_count: 0,
        from_stage: 'END_YEAR_REVIEW',
        to_stage: 'ARCHIVED',
      }
      vi.mocked(post).mockResolvedValue(mockResponse)

      const result = await bulkAdvanceStage({
        from_stage: 'END_YEAR_REVIEW',
      })

      expect(result.advanced_count).toBe(0)
    })
  })

  describe('getStageName', () => {
    it('should return "Goal Setting" for GOAL_SETTING', () => {
      expect(getStageName('GOAL_SETTING')).toBe('Goal Setting')
    })

    it('should return "Mid-Year Review" for MID_YEAR_REVIEW', () => {
      expect(getStageName('MID_YEAR_REVIEW')).toBe('Mid-Year Review')
    })

    it('should return "End-Year Review" for END_YEAR_REVIEW', () => {
      expect(getStageName('END_YEAR_REVIEW')).toBe('End-Year Review')
    })
  })

  describe('getNextStage', () => {
    it('should return MID_YEAR_REVIEW for GOAL_SETTING', () => {
      expect(getNextStage('GOAL_SETTING')).toBe('MID_YEAR_REVIEW')
    })

    it('should return END_YEAR_REVIEW for MID_YEAR_REVIEW', () => {
      expect(getNextStage('MID_YEAR_REVIEW')).toBe('END_YEAR_REVIEW')
    })

    it('should return ARCHIVED for END_YEAR_REVIEW', () => {
      expect(getNextStage('END_YEAR_REVIEW')).toBe('ARCHIVED')
    })

    it('should return null for unknown stages', () => {
      // @ts-expect-error Testing invalid stage
      expect(getNextStage('INVALID')).toBeNull()
    })
  })
})
