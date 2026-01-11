// TSS PPM v3.0 - ScoreAdjustmentPanel Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ScoreAdjustmentPanel from '../../components/calibration/ScoreAdjustmentPanel.vue'
import type { CalibrationReview } from '../../api/calibration'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'calibration.adjustment.title': 'Score Adjustment',
        'calibration.adjustment.employee': 'Employee',
        'calibration.adjustment.currentScores': 'Current Scores',
        'calibration.adjustment.whatScore': 'WHAT Score',
        'calibration.adjustment.howScore': 'HOW Score',
        'calibration.adjustment.newScores': 'New Scores',
        'calibration.adjustment.rationale': 'Rationale',
        'calibration.adjustment.rationalePlaceholder': 'Explain the reason for this adjustment...',
        'calibration.adjustment.rationaleRequired': 'Rationale is required',
        'calibration.adjustment.submit': 'Submit Adjustment',
        'calibration.adjustment.cancel': 'Cancel',
        'calibration.adjustment.submitting': 'Submitting...',
        'calibration.adjustment.success': 'Score adjustment saved',
        'calibration.adjustment.error': 'Failed to save adjustment',
        'calibration.adjustment.noChanges': 'No score changes made',
      }
      return messages[key] || key
    },
  }),
}))

// Mock the API
const mockAdjustScores = vi.fn()
vi.mock('../../api/calibration', () => ({
  adjustReviewScores: (sessionId: string, reviewId: string, data: unknown) =>
    mockAdjustScores(sessionId, reviewId, data),
}))

function createMockReview(overrides: Partial<CalibrationReview> = {}): CalibrationReview {
  return {
    review_id: 'review-1',
    employee_id: 'emp-1',
    employee_name: 'John Doe',
    employee_email: 'john@example.com',
    what_score: 2.0,
    how_score: 2.0,
    grid_position_what: 2,
    grid_position_how: 2,
    what_veto_active: false,
    how_veto_active: false,
    review_status: 'SIGNED',
    manager_first_name: 'Jane',
    manager_last_name: 'Smith',
    ...overrides,
  }
}

describe('ScoreAdjustmentPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAdjustScores.mockResolvedValue({
      adjustment_id: 'adj-1',
      what_score: 2.5,
      how_score: 2.5,
    })
  })

  function createWrapper(props: { sessionId: string; review: CalibrationReview }) {
    return mount(ScoreAdjustmentPanel, {
      props,
    })
  }

  describe('rendering', () => {
    it('should display employee name', () => {
      const review = createMockReview({ employee_name: 'John Doe' })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      expect(wrapper.text()).toContain('John Doe')
    })

    it('should display current WHAT score', () => {
      const review = createMockReview({ what_score: 2.5 })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      expect(wrapper.text()).toContain('2.5')
    })

    it('should display current HOW score', () => {
      const review = createMockReview({ how_score: 2.0 })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      expect(wrapper.text()).toContain('2.0')
    })

    it('should render WHAT score input', () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      const whatInput = wrapper.find('input[name="whatScore"]')
      expect(whatInput.exists()).toBe(true)
    })

    it('should render HOW score input', () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      const howInput = wrapper.find('input[name="howScore"]')
      expect(howInput.exists()).toBe(true)
    })

    it('should render rationale textarea', () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      const rationale = wrapper.find('textarea[name="rationale"]')
      expect(rationale.exists()).toBe(true)
    })

    it('should render submit button', () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      const submitBtn = wrapper.find('button[type="submit"]')
      expect(submitBtn.exists()).toBe(true)
    })

    it('should render cancel button', () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      const cancelBtn = wrapper.find('.cancel-btn')
      expect(cancelBtn.exists()).toBe(true)
    })
  })

  describe('score inputs', () => {
    it('should initialize WHAT score input with current value', () => {
      const review = createMockReview({ what_score: 2.5 })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      const whatInput = wrapper.find('input[name="whatScore"]')
      expect((whatInput.element as HTMLInputElement).value).toBe('2.5')
    })

    it('should initialize HOW score input with current value', () => {
      const review = createMockReview({ how_score: 2.0 })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      const howInput = wrapper.find('input[name="howScore"]')
      expect((howInput.element as HTMLInputElement).value).toBe('2')
    })

    it('should allow changing WHAT score', async () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview({ what_score: 2.0 }),
      })

      const whatInput = wrapper.find('input[name="whatScore"]')
      await whatInput.setValue('2.5')

      expect((whatInput.element as HTMLInputElement).value).toBe('2.5')
    })

    it('should allow changing HOW score', async () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview({ how_score: 2.0 }),
      })

      const howInput = wrapper.find('input[name="howScore"]')
      await howInput.setValue('2.5')

      expect((howInput.element as HTMLInputElement).value).toBe('2.5')
    })

    it('should constrain WHAT score between 1.0 and 3.0', () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      const whatInput = wrapper.find('input[name="whatScore"]')
      expect(whatInput.attributes('min')).toBe('1')
      expect(whatInput.attributes('max')).toBe('3')
    })

    it('should constrain HOW score between 1.0 and 3.0', () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      const howInput = wrapper.find('input[name="howScore"]')
      expect(howInput.attributes('min')).toBe('1')
      expect(howInput.attributes('max')).toBe('3')
    })
  })

  describe('rationale validation', () => {
    it('should show error when rationale is empty on submit', async () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      await wrapper.find('input[name="whatScore"]').setValue('2.5')
      await wrapper.find('form').trigger('submit')

      expect(wrapper.text()).toContain('Rationale is required')
    })

    it('should not submit when rationale is empty', async () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      await wrapper.find('input[name="whatScore"]').setValue('2.5')
      await wrapper.find('form').trigger('submit')

      expect(mockAdjustScores).not.toHaveBeenCalled()
    })

    it('should clear error when rationale is entered', async () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      await wrapper.find('input[name="whatScore"]').setValue('2.5')
      await wrapper.find('form').trigger('submit')
      expect(wrapper.text()).toContain('Rationale is required')

      await wrapper.find('textarea[name="rationale"]').setValue('Test rationale')
      expect(wrapper.text()).not.toContain('Rationale is required')
    })
  })

  describe('submission', () => {
    it('should call adjustReviewScores with correct parameters', async () => {
      const review = createMockReview({ review_id: 'rev-123', what_score: 2.0, how_score: 2.0 })
      const wrapper = createWrapper({ sessionId: 'session-456', review })

      await wrapper.find('input[name="whatScore"]').setValue('2.5')
      await wrapper.find('input[name="howScore"]').setValue('2.5')
      await wrapper.find('textarea[name="rationale"]').setValue('Performance improved')
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(mockAdjustScores).toHaveBeenCalledWith('session-456', 'rev-123', {
        what_score: 2.5,
        how_score: 2.5,
        rationale: 'Performance improved',
      })
    })

    it('should emit success event after successful submission', async () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      await wrapper.find('input[name="whatScore"]').setValue('2.5')
      await wrapper.find('textarea[name="rationale"]').setValue('Test')
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.emitted('success')).toBeTruthy()
    })

    it('should disable submit button while submitting', async () => {
      mockAdjustScores.mockReturnValue(new Promise(() => {})) // Never resolves
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      await wrapper.find('input[name="whatScore"]').setValue('2.5')
      await wrapper.find('textarea[name="rationale"]').setValue('Test')
      await wrapper.find('form').trigger('submit')

      const submitBtn = wrapper.find('button[type="submit"]')
      expect((submitBtn.element as HTMLButtonElement).disabled).toBe(true)
    })

    it('should show success message after submission', async () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      await wrapper.find('input[name="whatScore"]').setValue('2.5')
      await wrapper.find('textarea[name="rationale"]').setValue('Test')
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Score adjustment saved')
    })

    it('should show error message on API failure', async () => {
      mockAdjustScores.mockRejectedValue(new Error('API error'))
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      await wrapper.find('input[name="whatScore"]').setValue('2.5')
      await wrapper.find('textarea[name="rationale"]').setValue('Test')
      await wrapper.find('form').trigger('submit')
      await flushPromises()

      expect(wrapper.text()).toContain('Failed to save adjustment')
    })
  })

  describe('no changes validation', () => {
    it('should show message when no score changes made', async () => {
      const review = createMockReview({ what_score: 2.0, how_score: 2.0 })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      // Don't change any scores, just add rationale and submit
      await wrapper.find('textarea[name="rationale"]').setValue('Test')
      await wrapper.find('form').trigger('submit')

      expect(wrapper.text()).toContain('No score changes made')
    })

    it('should not submit when scores unchanged', async () => {
      const review = createMockReview({ what_score: 2.0, how_score: 2.0 })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      await wrapper.find('textarea[name="rationale"]').setValue('Test')
      await wrapper.find('form').trigger('submit')

      expect(mockAdjustScores).not.toHaveBeenCalled()
    })
  })

  describe('cancel button', () => {
    it('should emit cancel event when cancel clicked', async () => {
      const wrapper = createWrapper({
        sessionId: 'session-1',
        review: createMockReview(),
      })

      const cancelBtn = wrapper.find('.cancel-btn')
      await cancelBtn.trigger('click')

      expect(wrapper.emitted('cancel')).toHaveLength(1)
    })
  })

  describe('score change indicator', () => {
    it('should show change indicator when WHAT score differs', async () => {
      const review = createMockReview({ what_score: 2.0 })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      await wrapper.find('input[name="whatScore"]').setValue('2.5')

      const changeIndicator = wrapper.find('.what-change-indicator')
      expect(changeIndicator.exists()).toBe(true)
    })

    it('should show change indicator when HOW score differs', async () => {
      const review = createMockReview({ how_score: 2.0 })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      await wrapper.find('input[name="howScore"]').setValue('2.5')

      const changeIndicator = wrapper.find('.how-change-indicator')
      expect(changeIndicator.exists()).toBe(true)
    })

    it('should show positive/negative indicator for score increase', async () => {
      const review = createMockReview({ what_score: 2.0 })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      await wrapper.find('input[name="whatScore"]').setValue('2.5')

      const changeIndicator = wrapper.find('.what-change-indicator')
      expect(changeIndicator.classes()).toContain('positive')
    })

    it('should show negative indicator for score decrease', async () => {
      const review = createMockReview({ what_score: 2.5 })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      await wrapper.find('input[name="whatScore"]').setValue('2.0')

      const changeIndicator = wrapper.find('.what-change-indicator')
      expect(changeIndicator.classes()).toContain('negative')
    })
  })

  describe('null scores handling', () => {
    it('should handle null WHAT score', () => {
      const review = createMockReview({ what_score: null })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      const whatInput = wrapper.find('input[name="whatScore"]')
      expect((whatInput.element as HTMLInputElement).value).toBe('')
    })

    it('should handle null HOW score', () => {
      const review = createMockReview({ how_score: null })
      const wrapper = createWrapper({ sessionId: 'session-1', review })

      const howInput = wrapper.find('input[name="howScore"]')
      expect((howInput.element as HTMLInputElement).value).toBe('')
    })
  })
})
