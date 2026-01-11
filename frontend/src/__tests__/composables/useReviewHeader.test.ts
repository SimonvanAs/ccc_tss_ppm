// TSS PPM v3.0 - useReviewHeader Composable Tests
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { flushPromises } from '@vue/test-utils'
import { useReviewHeader } from '../../composables/useReviewHeader'
import * as reviewsApi from '../../api/reviews'

vi.mock('../../api/reviews', () => ({
  fetchReview: vi.fn(),
  updateReviewHeader: vi.fn(),
}))

describe('useReviewHeader', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  const mockReview: reviewsApi.ReviewDetails = {
    id: 'review-123',
    employee_id: 'emp-1',
    manager_id: 'mgr-1',
    status: 'DRAFT',
    stage: 'GOAL_SETTING',
    review_year: 2026,
    tov_level: 'B',
    job_title: 'Developer',
    what_score: null,
    how_score: null,
    employee_name: 'John Doe',
    manager_name: 'Jane Smith',
    employee_signature_date: null,
    employee_signature_by: null,
    manager_signature_date: null,
    manager_signature_by: null,
    rejection_feedback: null,
    goal_setting_completed_at: null,
    mid_year_completed_at: null,
    end_year_completed_at: null,
  }

  describe('loadReview', () => {
    it('should load review data and populate refs', async () => {
      vi.mocked(reviewsApi.fetchReview).mockResolvedValue(mockReview)

      const { review, loading, loadReview } = useReviewHeader('review-123')

      expect(loading.value).toBe(false)

      const loadPromise = loadReview()
      expect(loading.value).toBe(true)

      await loadPromise
      await flushPromises()

      expect(loading.value).toBe(false)
      expect(review.value).toEqual(mockReview)
    })
  })

  describe('job_title auto-save', () => {
    it('should trigger auto-save when job_title changes', async () => {
      vi.mocked(reviewsApi.fetchReview).mockResolvedValue(mockReview)
      vi.mocked(reviewsApi.updateReviewHeader).mockResolvedValue({
        ...mockReview,
        job_title: 'Senior Developer',
      })

      const { loadReview, updateJobTitle } = useReviewHeader('review-123')
      await loadReview()

      updateJobTitle('Senior Developer')

      // Advance timers past debounce
      await vi.advanceTimersByTimeAsync(3000)
      await flushPromises()

      expect(reviewsApi.updateReviewHeader).toHaveBeenCalledWith('review-123', {
        job_title: 'Senior Developer',
      })
    })

    it('should debounce multiple job_title changes', async () => {
      vi.mocked(reviewsApi.fetchReview).mockResolvedValue(mockReview)
      vi.mocked(reviewsApi.updateReviewHeader).mockResolvedValue({
        ...mockReview,
        job_title: 'Final Title',
      })

      const { loadReview, updateJobTitle } = useReviewHeader('review-123')
      await loadReview()

      // Rapid changes
      updateJobTitle('First')
      await vi.advanceTimersByTimeAsync(500)
      updateJobTitle('Second')
      await vi.advanceTimersByTimeAsync(500)
      updateJobTitle('Final Title')

      // Should not have called API yet
      expect(reviewsApi.updateReviewHeader).not.toHaveBeenCalled()

      // Advance past debounce
      await vi.advanceTimersByTimeAsync(3000)
      await flushPromises()

      // Should only call once with final value
      expect(reviewsApi.updateReviewHeader).toHaveBeenCalledTimes(1)
      expect(reviewsApi.updateReviewHeader).toHaveBeenCalledWith('review-123', {
        job_title: 'Final Title',
      })
    })
  })

  describe('tov_level auto-save', () => {
    it('should trigger auto-save when tov_level changes', async () => {
      vi.mocked(reviewsApi.fetchReview).mockResolvedValue(mockReview)
      vi.mocked(reviewsApi.updateReviewHeader).mockResolvedValue({
        ...mockReview,
        tov_level: 'C',
      })

      const { loadReview, updateTovLevel } = useReviewHeader('review-123')
      await loadReview()

      updateTovLevel('C')

      // Advance timers past debounce
      await vi.advanceTimersByTimeAsync(3000)
      await flushPromises()

      expect(reviewsApi.updateReviewHeader).toHaveBeenCalledWith('review-123', {
        tov_level: 'C',
      })
    })

    it('should debounce multiple tov_level changes', async () => {
      vi.mocked(reviewsApi.fetchReview).mockResolvedValue(mockReview)
      vi.mocked(reviewsApi.updateReviewHeader).mockResolvedValue({
        ...mockReview,
        tov_level: 'D',
      })

      const { loadReview, updateTovLevel } = useReviewHeader('review-123')
      await loadReview()

      updateTovLevel('A')
      await vi.advanceTimersByTimeAsync(500)
      updateTovLevel('B')
      await vi.advanceTimersByTimeAsync(500)
      updateTovLevel('D')

      // Advance past debounce
      await vi.advanceTimersByTimeAsync(3000)
      await flushPromises()

      expect(reviewsApi.updateReviewHeader).toHaveBeenCalledTimes(1)
      expect(reviewsApi.updateReviewHeader).toHaveBeenCalledWith('review-123', {
        tov_level: 'D',
      })
    })
  })

  describe('SaveIndicator integration', () => {
    it('should expose save status for SaveIndicator', async () => {
      vi.mocked(reviewsApi.fetchReview).mockResolvedValue(mockReview)
      vi.mocked(reviewsApi.updateReviewHeader).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(mockReview), 100))
      )

      const { loadReview, updateJobTitle, saveStatus } = useReviewHeader('review-123')
      await loadReview()

      expect(saveStatus.value).toBe('idle')

      updateJobTitle('New Title')
      await vi.advanceTimersByTimeAsync(2500) // Trigger debounce

      expect(saveStatus.value).toBe('saving')

      await vi.advanceTimersByTimeAsync(200) // Complete save
      await flushPromises()

      expect(saveStatus.value).toBe('saved')
    })

    it('should show error status on save failure', async () => {
      vi.mocked(reviewsApi.fetchReview).mockResolvedValue(mockReview)
      vi.mocked(reviewsApi.updateReviewHeader).mockRejectedValue(new Error('Network error'))

      const { loadReview, updateJobTitle, saveStatus } = useReviewHeader('review-123')
      await loadReview()

      updateJobTitle('New Title')
      await vi.advanceTimersByTimeAsync(3000)
      await flushPromises()

      expect(saveStatus.value).toBe('error')
    })
  })
})
