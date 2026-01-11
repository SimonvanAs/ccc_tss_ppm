// TSS PPM v3.0 - GoalSettingView Submission Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import GoalSettingView from '../../views/GoalSettingView.vue'
import { GoalType } from '../../types'
import type { Goal } from '../../types'
import type { Competency } from '../../types/competency'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string, params?: Record<string, unknown>) => {
      const messages: Record<string, string> = {
        'goals.pageTitle': 'Set Your Goals',
        'goals.pageSubtitle': 'Define your objectives for this review period',
        'goals.addGoal': 'Add Goal',
        'goals.edit': 'Edit Goal',
        'goals.deleteGoal': 'Delete Goal',
        'goals.submit': 'Submit Goals',
        'goals.submitHint': 'Goal weights must total 100% before submitting',
        'goals.submitting': 'Submitting...',
        'goals.submitSuccess': 'Goals submitted successfully',
        'goals.confirmDelete': `Are you sure you want to delete "${params?.title}"?`,
        'actions.delete': 'Delete',
        'actions.cancel': 'Cancel',
        'errors.generic': 'An error occurred',
        'errors.submitFailed': 'Failed to submit goals',
        'goals.headerFieldsRequired': 'Job title and TOV level are required',
        'competencyPreview.title': 'Competencies for Selected Level',
        'competencyPreview.selectTovLevel': 'Select a TOV level',
        'competencyPreview.emptyState': 'No competencies available',
        'competencies.categories.Dedicated': 'Dedicated',
        'competencies.categories.Entrepreneurial': 'Entrepreneurial',
        'competencies.categories.Innovative': 'Innovative',
        'common.loading': 'Loading...',
      }
      return messages[key] || key
    },
  }),
}))

// Mock vue-router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

// Mock goals API
vi.mock('../../api/goals', () => ({
  fetchGoals: vi.fn(),
  createGoal: vi.fn(),
  updateGoal: vi.fn(),
  deleteGoal: vi.fn(),
  reorderGoals: vi.fn(),
  submitReview: vi.fn(),
}))

// Mock competencies API
vi.mock('../../api/competencies', () => ({
  getCompetencies: vi.fn(),
}))

// Mock reviews API
vi.mock('../../api/reviews', () => ({
  fetchReview: vi.fn(),
  updateReviewHeader: vi.fn(),
}))

import * as goalsApi from '../../api/goals'
import * as competenciesApi from '../../api/competencies'
import * as reviewsApi from '../../api/reviews'

function createMockGoals(): Goal[] {
  return [
    {
      id: 'goal-1',
      review_id: 'review-123',
      title: 'First Goal',
      description: 'Description 1',
      goal_type: GoalType.STANDARD,
      weight: 50,
      order_index: 0,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 'goal-2',
      review_id: 'review-123',
      title: 'Second Goal',
      description: 'Description 2',
      goal_type: GoalType.KAR,
      weight: 50,
      order_index: 1,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
  ]
}

function createInvalidWeightGoals(): Goal[] {
  return [
    {
      id: 'goal-1',
      review_id: 'review-123',
      title: 'First Goal',
      goal_type: GoalType.STANDARD,
      weight: 30,
      order_index: 0,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
  ]
}

function createMockReview(overrides: Partial<{
  job_title: string | null
  tov_level: string | null
  status: string
}> = {}) {
  return {
    id: 'review-123',
    employee_id: 'emp-456',
    manager_id: 'mgr-789',
    status: overrides.status !== undefined ? overrides.status : 'DRAFT',
    stage: 'GOAL_SETTING',
    review_year: 2026,
    job_title: 'job_title' in overrides ? overrides.job_title : 'Software Engineer',
    tov_level: 'tov_level' in overrides ? overrides.tov_level : 'B',
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
}

describe('GoalSettingView - Submission', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    mockPush.mockReset()
  })

  function createWrapper(goals: Goal[] = createMockGoals()) {
    vi.mocked(goalsApi.fetchGoals).mockResolvedValue(goals)
    // Mock review with valid header fields so canSubmit works
    vi.mocked(reviewsApi.fetchReview).mockResolvedValue(createMockReview())
    // Mock competencies to avoid undefined errors
    vi.mocked(competenciesApi.getCompetencies).mockResolvedValue([])

    return mount(GoalSettingView, {
      props: {
        reviewId: 'review-123',
      },
      global: {
        stubs: {
          Modal: {
            template: '<div class="modal-stub"><slot /></div>',
            props: ['show', 'title'],
          },
          ConfirmDialog: {
            template: '<div class="confirm-stub"></div>',
            props: ['show', 'title', 'message', 'confirmText', 'danger'],
          },
          teleport: true,
        },
      },
    })
  }

  describe('submit button state', () => {
    it('should disable submit button when weights do not total 100%', async () => {
      const wrapper = createWrapper(createInvalidWeightGoals())
      await flushPromises()

      const submitButton = wrapper.find('.btn-submit')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should enable submit button when weights total 100%', async () => {
      const wrapper = createWrapper(createMockGoals())
      await flushPromises()

      const submitButton = wrapper.find('.btn-submit')
      expect(submitButton.attributes('disabled')).toBeUndefined()
    })

    it('should show hint when weights are invalid', async () => {
      const wrapper = createWrapper(createInvalidWeightGoals())
      await flushPromises()

      expect(wrapper.text()).toContain('Goal weights must total 100%')
    })

    it('should hide hint when weights are valid', async () => {
      const wrapper = createWrapper(createMockGoals())
      await flushPromises()

      expect(wrapper.text()).not.toContain('Goal weights must total 100%')
    })
  })

  describe('submit flow', () => {
    it('should call submitReview API when submit clicked', async () => {
      vi.mocked(goalsApi.submitReview).mockResolvedValueOnce(undefined)
      const wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('.btn-submit').trigger('click')
      await flushPromises()

      expect(goalsApi.submitReview).toHaveBeenCalledWith('review-123')
    })

    it('should show submitting state during submission', async () => {
      let resolveSubmit: () => void
      vi.mocked(goalsApi.submitReview).mockImplementation(
        () => new Promise((resolve) => { resolveSubmit = resolve })
      )
      const wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('.btn-submit').trigger('click')
      await nextTick()

      expect(wrapper.find('.btn-submit').text()).toContain('Submitting')

      resolveSubmit!()
      await flushPromises()
    })

    it('should disable submit button during submission', async () => {
      let resolveSubmit: () => void
      vi.mocked(goalsApi.submitReview).mockImplementation(
        () => new Promise((resolve) => { resolveSubmit = resolve })
      )
      const wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('.btn-submit').trigger('click')
      await nextTick()

      expect(wrapper.find('.btn-submit').attributes('disabled')).toBeDefined()

      resolveSubmit!()
      await flushPromises()
    })

    it('should show success message after successful submission', async () => {
      vi.mocked(goalsApi.submitReview).mockResolvedValueOnce(undefined)
      const wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('.btn-submit').trigger('click')
      await flushPromises()

      expect(wrapper.text()).toContain('Goals submitted successfully')
    })

    it('should navigate to dashboard after successful submission', async () => {
      vi.useFakeTimers()
      vi.mocked(goalsApi.submitReview).mockResolvedValueOnce(undefined)
      const wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('.btn-submit').trigger('click')
      await flushPromises()

      // Fast-forward the navigation timeout
      vi.advanceTimersByTime(1500)
      await flushPromises()

      expect(mockPush).toHaveBeenCalledWith({ name: 'dashboard' })
      vi.useRealTimers()
    })

    it('should show error message on submission failure', async () => {
      vi.mocked(goalsApi.submitReview).mockRejectedValueOnce(new Error('Network error'))
      const wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('.btn-submit').trigger('click')
      await flushPromises()

      expect(wrapper.text()).toContain('Failed to submit')
    })

    it('should re-enable submit button after error', async () => {
      vi.mocked(goalsApi.submitReview).mockRejectedValueOnce(new Error('Network error'))
      const wrapper = createWrapper()
      await flushPromises()

      await wrapper.find('.btn-submit').trigger('click')
      await flushPromises()

      const submitButton = wrapper.find('.btn-submit')
      expect(submitButton.attributes('disabled')).toBeUndefined()
    })
  })
})

const mockCompetencies: Competency[] = [
  {
    id: 'comp-1',
    level: 'B',
    category: 'Dedicated',
    subcategory: 'Result driven',
    title_en: 'Achieves Results',
    indicators_en: ['Delivers on commitments'],
    display_order: 1,
  },
  {
    id: 'comp-2',
    level: 'B',
    category: 'Entrepreneurial',
    subcategory: 'Entrepreneurial',
    title_en: 'Takes Initiative',
    indicators_en: ['Identifies opportunities'],
    display_order: 2,
  },
  {
    id: 'comp-3',
    level: 'B',
    category: 'Innovative',
    subcategory: 'Market oriented',
    title_en: 'Understands Market',
    indicators_en: ['Monitors trends'],
    display_order: 3,
  },
]

describe('GoalSettingView - Competency Preview Integration', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  function createWrapperWithReview(goals: Goal[] = createMockGoals()) {
    vi.mocked(goalsApi.fetchGoals).mockResolvedValue(goals)
    vi.mocked(competenciesApi.getCompetencies).mockResolvedValue(mockCompetencies)

    return mount(GoalSettingView, {
      props: {
        reviewId: 'review-123',
      },
      global: {
        stubs: {
          Modal: {
            template: '<div class="modal-stub"><slot /></div>',
            props: ['show', 'title'],
          },
          ConfirmDialog: {
            template: '<div class="confirm-stub"></div>',
            props: ['show', 'title', 'message', 'confirmText', 'danger'],
          },
          teleport: true,
        },
      },
    })
  }

  it('should render CompetencyPreview component', async () => {
    const wrapper = createWrapperWithReview()
    await flushPromises()

    expect(wrapper.find('[data-testid="competency-preview"]').exists()).toBe(true)
  })

  it('should display competency preview title', async () => {
    const wrapper = createWrapperWithReview()
    await flushPromises()

    expect(wrapper.text()).toContain('Competencies for Selected Level')
  })
})

describe('GoalSettingView - Header Field Validation', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  function createWrapperWithValidation(
    goals: Goal[] = createMockGoals(),
    reviewOverrides: Partial<{ job_title: string | null; tov_level: string | null }> = {}
  ) {
    vi.mocked(goalsApi.fetchGoals).mockResolvedValue(goals)
    vi.mocked(competenciesApi.getCompetencies).mockResolvedValue(mockCompetencies)
    vi.mocked(reviewsApi.fetchReview).mockResolvedValue(createMockReview(reviewOverrides))

    return mount(GoalSettingView, {
      props: {
        reviewId: 'review-123',
      },
      global: {
        stubs: {
          Modal: {
            template: '<div class="modal-stub"><slot /></div>',
            props: ['show', 'title'],
          },
          ConfirmDialog: {
            template: '<div class="confirm-stub"></div>',
            props: ['show', 'title', 'message', 'confirmText', 'danger'],
          },
          teleport: true,
        },
      },
    })
  }

  describe('submit button disabled when job_title empty', () => {
    it('should disable submit button when job_title is null', async () => {
      const wrapper = createWrapperWithValidation(createMockGoals(), { job_title: null })
      await flushPromises()

      const submitButton = wrapper.find('.btn-submit')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should disable submit button when job_title is empty string', async () => {
      const wrapper = createWrapperWithValidation(createMockGoals(), { job_title: '' })
      await flushPromises()

      const submitButton = wrapper.find('.btn-submit')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })
  })

  describe('submit button disabled when tov_level empty', () => {
    it('should disable submit button when tov_level is null', async () => {
      const wrapper = createWrapperWithValidation(createMockGoals(), { tov_level: null })
      await flushPromises()

      const submitButton = wrapper.find('.btn-submit')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should disable submit button when tov_level is empty string', async () => {
      const wrapper = createWrapperWithValidation(createMockGoals(), { tov_level: '' })
      await flushPromises()

      const submitButton = wrapper.find('.btn-submit')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })
  })

  describe('validation error messages display', () => {
    it('should show validation hint when job_title is missing', async () => {
      const wrapper = createWrapperWithValidation(createMockGoals(), { job_title: null })
      await flushPromises()

      expect(wrapper.text()).toContain('Job title and TOV level are required')
    })

    it('should show validation hint when tov_level is missing', async () => {
      const wrapper = createWrapperWithValidation(createMockGoals(), { tov_level: null })
      await flushPromises()

      expect(wrapper.text()).toContain('Job title and TOV level are required')
    })

    it('should not show header validation hint when both fields are set', async () => {
      const wrapper = createWrapperWithValidation(createMockGoals(), {
        job_title: 'Engineer',
        tov_level: 'B',
      })
      await flushPromises()

      expect(wrapper.text()).not.toContain('Job title and TOV level are required')
    })
  })

  describe('submit enabled when all validations pass', () => {
    it('should enable submit when weights valid and header fields set', async () => {
      const wrapper = createWrapperWithValidation(createMockGoals(), {
        job_title: 'Engineer',
        tov_level: 'B',
      })
      await flushPromises()

      const submitButton = wrapper.find('.btn-submit')
      expect(submitButton.attributes('disabled')).toBeUndefined()
    })
  })
})
