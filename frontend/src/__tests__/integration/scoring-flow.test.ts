// TSS PPM v3.0 - Scoring Flow Integration Tests
// These tests validate the complete scoring workflow scenarios
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import ReviewScoringView from '../../views/ReviewScoringView.vue'
import * as scoresApi from '../../api/scores'

// Mock the API
vi.mock('../../api/scores', () => ({
  fetchScores: vi.fn(),
  saveScores: vi.fn(),
  submitScores: vi.fn(),
}))

// Mock vue-router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: { reviewId: 'review-123' },
  }),
  useRouter: () => ({
    push: mockPush,
  }),
}))

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
    locale: { value: 'en' },
  }),
}))

const mockGoals = [
  { id: 'goal-1', title: 'Revenue Target', weight: 40, goal_type: 'STANDARD' },
  { id: 'goal-2', title: 'Safety Compliance', weight: 30, goal_type: 'SCF' },
  { id: 'goal-3', title: 'Key Action', weight: 30, goal_type: 'KAR' },
]

const mockCompetencies = [
  { id: 'comp-1', name: 'Result Driven', category: 'Dedicated' },
  { id: 'comp-2', name: 'Committed', category: 'Dedicated' },
  { id: 'comp-3', name: 'Entrepreneurial', category: 'Entrepreneurial' },
  { id: 'comp-4', name: 'Ambition', category: 'Entrepreneurial' },
  { id: 'comp-5', name: 'Market Oriented', category: 'Innovative' },
  { id: 'comp-6', name: 'Customer Focused', category: 'Innovative' },
]

describe('Scoring Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockPush.mockClear()
    vi.mocked(scoresApi.fetchScores).mockResolvedValue({
      goal_scores: [],
      competency_scores: [],
    })
    vi.mocked(scoresApi.saveScores).mockResolvedValue({
      goal_scores: [],
      competency_scores: [],
    })
    vi.mocked(scoresApi.submitScores).mockResolvedValue({
      status: 'PENDING_EMPLOYEE_SIGNATURE',
    })
  })

  describe('complete scoring flow', () => {
    it('should load existing scores on mount', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [
          { goal_id: 'goal-1', score: 2, feedback: 'Good progress' },
        ],
        competency_scores: [
          { competency_id: 'comp-1', score: 3 },
        ],
      })

      mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      expect(scoresApi.fetchScores).toHaveBeenCalledWith('review-123')
    })

    it('should display NineGrid and ScoreSummary in sidebar', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      expect(wrapper.findComponent({ name: 'NineGrid' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'ScoreSummary' }).exists()).toBe(true)
    })
  })

  describe('auto-save functionality', () => {
    it('should trigger save when scores change', async () => {
      vi.useFakeTimers()

      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      // Find and interact with GoalScoringSection
      const goalSection = wrapper.findComponent({ name: 'GoalScoringSection' })
      expect(goalSection.exists()).toBe(true)

      // Emit a score change
      await goalSection.vm.$emit('score-change', 'goal-1', 2)

      // Wait for debounce (500ms in useScoring)
      vi.advanceTimersByTime(600)
      await flushPromises()

      // SaveScores should have been called
      expect(scoresApi.saveScores).toHaveBeenCalled()

      vi.useRealTimers()
    })
  })

  describe('VETO scenarios', () => {
    it('should show VETO indicator when SCF goal scores 1', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [
          { goal_id: 'goal-1', score: 3 },
          { goal_id: 'goal-2', score: 1 }, // SCF goal with score 1 = VETO
          { goal_id: 'goal-3', score: 2 },
        ],
        competency_scores: mockCompetencies.map((c) => ({
          competency_id: c.id,
          score: 2,
        })),
      })

      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      // NineGrid should show veto
      const nineGrid = wrapper.findComponent({ name: 'NineGrid' })
      expect(nineGrid.props('vetoActive')).toBe(true)
    })

    it('should show VETO when competency scores 1', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: mockGoals.map((g) => ({
          goal_id: g.id,
          score: 2,
        })),
        competency_scores: [
          { competency_id: 'comp-1', score: 1 }, // Score 1 = VETO
          { competency_id: 'comp-2', score: 2 },
          { competency_id: 'comp-3', score: 2 },
          { competency_id: 'comp-4', score: 2 },
          { competency_id: 'comp-5', score: 2 },
          { competency_id: 'comp-6', score: 2 },
        ],
      })

      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      const nineGrid = wrapper.findComponent({ name: 'NineGrid' })
      expect(nineGrid.props('vetoActive')).toBe(true)
    })
  })

  describe('submit scores flow', () => {
    it('should show SubmitScoresButton when not read-only', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies, readOnly: false },
      })
      await flushPromises()

      expect(wrapper.findComponent({ name: 'SubmitScoresButton' }).exists()).toBe(true)
    })

    it('should not show SubmitScoresButton in read-only mode', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies, readOnly: true },
      })
      await flushPromises()

      expect(wrapper.findComponent({ name: 'SubmitScoresButton' }).exists()).toBe(false)
    })

    it('should disable submit button when scores incomplete', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      const submitButton = wrapper.findComponent({ name: 'SubmitScoresButton' })
      expect(submitButton.props('allScoresComplete')).toBe(false)
    })

    it('should redirect to team dashboard after successful submit', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: mockGoals.map((g) => ({
          goal_id: g.id,
          score: 2,
        })),
        competency_scores: mockCompetencies.map((c) => ({
          competency_id: c.id,
          score: 2,
        })),
      })

      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      // Trigger submit
      const submitButton = wrapper.findComponent({ name: 'SubmitScoresButton' })
      await submitButton.vm.$emit('submit')
      await flushPromises()

      expect(scoresApi.submitScores).toHaveBeenCalledWith('review-123')
      expect(mockPush).toHaveBeenCalledWith('/team')
    })

    it('should handle submit error gracefully', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: mockGoals.map((g) => ({
          goal_id: g.id,
          score: 2,
        })),
        competency_scores: mockCompetencies.map((c) => ({
          competency_id: c.id,
          score: 2,
        })),
      })
      vi.mocked(scoresApi.submitScores).mockRejectedValue(new Error('Submission failed'))

      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      // Trigger submit
      const submitButton = wrapper.findComponent({ name: 'SubmitScoresButton' })
      await submitButton.vm.$emit('submit')
      await flushPromises()

      // Should not navigate on error
      expect(mockPush).not.toHaveBeenCalled()
    })
  })

  describe('read-only mode', () => {
    it('should disable scoring sections in read-only mode', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies, readOnly: true },
      })
      await flushPromises()

      const goalSection = wrapper.findComponent({ name: 'GoalScoringSection' })
      const compSection = wrapper.findComponent({ name: 'CompetencyScoringSection' })

      expect(goalSection.props('disabled')).toBe(true)
      expect(compSection.props('disabled')).toBe(true)
    })

    it('should still display scores in read-only mode', async () => {
      vi.mocked(scoresApi.fetchScores).mockResolvedValue({
        goal_scores: [{ goal_id: 'goal-1', score: 3, feedback: 'Excellent' }],
        competency_scores: [{ competency_id: 'comp-1', score: 2 }],
      })

      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies, readOnly: true },
      })
      await flushPromises()

      // Should still load and display scores
      expect(scoresApi.fetchScores).toHaveBeenCalled()
      expect(wrapper.findComponent({ name: 'NineGrid' }).exists()).toBe(true)
    })
  })
})
