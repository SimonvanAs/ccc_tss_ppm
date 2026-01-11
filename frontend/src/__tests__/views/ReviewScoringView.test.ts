// TSS PPM v3.0 - ReviewScoringView Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import ReviewScoringView from '../../views/ReviewScoringView.vue'
import * as scoresApi from '../../api/scores'

// Mock the API
vi.mock('../../api/scores', () => ({
  fetchScores: vi.fn(),
  saveScores: vi.fn(),
}))

// Mock vue-router
vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: { reviewId: 'review-123' },
  }),
  useRouter: () => ({
    push: vi.fn(),
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
  { id: 'goal-1', title: 'Revenue', weight: 50, goal_type: 'STANDARD' },
  { id: 'goal-2', title: 'Safety', weight: 50, goal_type: 'SCF' },
]

const mockCompetencies = [
  { id: 'comp-1', name: 'Result Driven', category: 'Dedicated' },
  { id: 'comp-2', name: 'Customer Focused', category: 'Innovative' },
]

describe('ReviewScoringView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(scoresApi.fetchScores).mockResolvedValue({
      goal_scores: [],
      competency_scores: [],
    })
    vi.mocked(scoresApi.saveScores).mockResolvedValue({
      goal_scores: [],
      competency_scores: [],
    })
  })

  describe('page integration', () => {
    it('should render page title', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      expect(wrapper.text()).toContain('Score Review')
    })

    it('should render GoalScoringSection', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      expect(wrapper.findComponent({ name: 'GoalScoringSection' }).exists()).toBe(true)
    })

    it('should render CompetencyScoringSection', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      expect(wrapper.findComponent({ name: 'CompetencyScoringSection' }).exists()).toBe(true)
    })

    it('should load existing scores on mount', async () => {
      mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      expect(scoresApi.fetchScores).toHaveBeenCalledWith('review-123')
    })
  })

  describe('auto-save status indicator', () => {
    it('should render SaveIndicator component', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      expect(wrapper.findComponent({ name: 'SaveIndicator' }).exists()).toBe(true)
    })
  })

  describe('9-Grid sidebar integration', () => {
    it('should render NineGrid in sidebar', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      expect(wrapper.findComponent({ name: 'NineGrid' }).exists()).toBe(true)
    })

    it('should render ScoreSummary in sidebar', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      expect(wrapper.findComponent({ name: 'ScoreSummary' }).exists()).toBe(true)
    })
  })

  describe('loading state', () => {
    it('should show loading indicator while fetching scores', async () => {
      let resolvePromise: (value: any) => void
      vi.mocked(scoresApi.fetchScores).mockReturnValue(
        new Promise((resolve) => {
          resolvePromise = resolve
        })
      )

      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })

      // Wait for Vue reactivity to update DOM (but not for fetchScores to resolve)
      await nextTick()

      expect(wrapper.find('.loading-state').exists()).toBe(true)

      resolvePromise!({ goal_scores: [], competency_scores: [] })
      await flushPromises()

      expect(wrapper.find('.loading-state').exists()).toBe(false)
    })
  })

  describe('error state', () => {
    it('should show error message on load failure', async () => {
      vi.mocked(scoresApi.fetchScores).mockRejectedValue(new Error('Failed to load'))

      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      expect(wrapper.find('.error-state').exists()).toBe(true)
      expect(wrapper.text()).toContain('Failed to load')
    })
  })

  describe('read-only mode', () => {
    it('should pass disabled=true to GoalScoringSection when readOnly is true', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies, readOnly: true },
      })
      await flushPromises()

      const goalSection = wrapper.findComponent({ name: 'GoalScoringSection' })
      expect(goalSection.props('disabled')).toBe(true)
    })

    it('should pass disabled=true to CompetencyScoringSection when readOnly is true', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies, readOnly: true },
      })
      await flushPromises()

      const compSection = wrapper.findComponent({ name: 'CompetencyScoringSection' })
      expect(compSection.props('disabled')).toBe(true)
    })

    it('should hide submit button when readOnly is true', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies, readOnly: true },
      })
      await flushPromises()

      expect(wrapper.findComponent({ name: 'SubmitScoresButton' }).exists()).toBe(false)
    })
  })

  describe('submit button', () => {
    it('should render SubmitScoresButton when not readOnly', async () => {
      const wrapper = mount(ReviewScoringView, {
        props: { goals: mockGoals, competencies: mockCompetencies },
      })
      await flushPromises()

      expect(wrapper.findComponent({ name: 'SubmitScoresButton' }).exists()).toBe(true)
    })
  })
})
