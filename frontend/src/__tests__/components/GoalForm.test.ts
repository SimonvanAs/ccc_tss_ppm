// TSS PPM v3.0 - GoalForm Component Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref, nextTick } from 'vue'
import GoalForm from '../../components/review/GoalForm.vue'
import { GoalType } from '../../types'
import type { Goal } from '../../types'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string, params?: Record<string, unknown>) => {
      const messages: Record<string, string> = {
        'goals.goalTitle': 'Goal Title',
        'goals.description': 'Description',
        'goals.type': 'Type',
        'goals.weight': 'Weight',
        'goals.types.STANDARD': 'Standard',
        'goals.types.KAR': 'Key Action Required',
        'goals.types.SCF': 'Strategic Critical Factor',
        'actions.save': 'Save',
        'actions.cancel': 'Cancel',
        'review.saving': 'Saving...',
        'validation.required': 'This field is required',
        'validation.maxLength': `Maximum ${params?.max} characters`,
        'validation.weightRange': 'Weight must be between 5 and 100',
        'goals.form.weightStep': 'Weight must be a multiple of 5',
        'goals.form.titlePlaceholder': 'Enter goal title',
        'goals.form.descriptionPlaceholder': 'Enter goal description (optional)',
      }
      return messages[key] || key
    },
  }),
}))

describe('GoalForm', () => {
  const defaultProps = {
    reviewId: 'review-123',
  }

  function createWrapper(props = {}) {
    return mount(GoalForm, {
      props: { ...defaultProps, ...props },
    })
  }

  describe('rendering', () => {
    it('should render title input field', () => {
      const wrapper = createWrapper()

      const titleInput = wrapper.find('input[name="title"]')
      expect(titleInput.exists()).toBe(true)
    })

    it('should render description textarea', () => {
      const wrapper = createWrapper()

      const descriptionTextarea = wrapper.find('textarea[name="description"]')
      expect(descriptionTextarea.exists()).toBe(true)
    })

    it('should render goal type dropdown with all options', () => {
      const wrapper = createWrapper()

      const typeSelect = wrapper.find('select[name="goal_type"]')
      expect(typeSelect.exists()).toBe(true)

      const options = typeSelect.findAll('option')
      expect(options).toHaveLength(3)
      expect(options[0].text()).toContain('Standard')
      expect(options[1].text()).toContain('Key Action')
      expect(options[2].text()).toContain('Strategic')
    })

    it('should render weight input with constraints', () => {
      const wrapper = createWrapper()

      const weightInput = wrapper.find('input[name="weight"]')
      expect(weightInput.exists()).toBe(true)
      expect(weightInput.attributes('type')).toBe('number')
      expect(weightInput.attributes('min')).toBe('5')
      expect(weightInput.attributes('max')).toBe('100')
      expect(weightInput.attributes('step')).toBe('5')
    })

    it('should render save and cancel buttons', () => {
      const wrapper = createWrapper()

      const saveButton = wrapper.find('button[type="submit"]')
      const cancelButton = wrapper.find('.form-actions button.btn-secondary')

      expect(saveButton.exists()).toBe(true)
      expect(cancelButton.exists()).toBe(true)
      expect(saveButton.text()).toContain('Save')
      expect(cancelButton.text()).toContain('Cancel')
    })
  })

  describe('default values', () => {
    it('should have empty title by default', () => {
      const wrapper = createWrapper()

      const titleInput = wrapper.find('input[name="title"]')
      expect((titleInput.element as HTMLInputElement).value).toBe('')
    })

    it('should have STANDARD as default goal type', () => {
      const wrapper = createWrapper()

      const typeSelect = wrapper.find('select[name="goal_type"]')
      expect((typeSelect.element as HTMLSelectElement).value).toBe(GoalType.STANDARD)
    })

    it('should have default weight of 20', () => {
      const wrapper = createWrapper()

      const weightInput = wrapper.find('input[name="weight"]')
      expect((weightInput.element as HTMLInputElement).value).toBe('20')
    })
  })

  describe('edit mode', () => {
    const existingGoal: Goal = {
      id: 'goal-1',
      review_id: 'review-123',
      title: 'Existing Goal',
      description: 'Goal description',
      goal_type: GoalType.KAR,
      weight: 35,
      score: null,
      display_order: 0,
    }

    it('should populate form with existing goal data', () => {
      const wrapper = createWrapper({ goal: existingGoal })

      const titleInput = wrapper.find('input[name="title"]')
      const descriptionTextarea = wrapper.find('textarea[name="description"]')
      const typeSelect = wrapper.find('select[name="goal_type"]')
      const weightInput = wrapper.find('input[name="weight"]')

      expect((titleInput.element as HTMLInputElement).value).toBe('Existing Goal')
      expect((descriptionTextarea.element as HTMLTextAreaElement).value).toBe('Goal description')
      expect((typeSelect.element as HTMLSelectElement).value).toBe(GoalType.KAR)
      expect((weightInput.element as HTMLInputElement).value).toBe('35')
    })

    it('should handle null description', () => {
      const goalWithNullDescription = { ...existingGoal, description: null }
      const wrapper = createWrapper({ goal: goalWithNullDescription })

      const descriptionTextarea = wrapper.find('textarea[name="description"]')
      expect((descriptionTextarea.element as HTMLTextAreaElement).value).toBe('')
    })
  })

  describe('validation', () => {
    it('should show error when title is empty on submit', async () => {
      const wrapper = createWrapper()

      // Submit form with empty title
      await wrapper.find('form').trigger('submit')
      await nextTick()

      const errorMessage = wrapper.find('.error-message')
      expect(errorMessage.exists()).toBe(true)
      expect(errorMessage.text()).toContain('required')
    })

    it('should show error when title exceeds 500 characters', async () => {
      const wrapper = createWrapper()

      const titleInput = wrapper.find('input[name="title"]')
      await titleInput.setValue('a'.repeat(501))
      await wrapper.find('form').trigger('submit')
      await nextTick()

      const errorMessage = wrapper.find('.error-message')
      expect(errorMessage.exists()).toBe(true)
      expect(errorMessage.text()).toContain('500')
    })

    it('should show error when weight is not multiple of 5', async () => {
      const wrapper = createWrapper()

      const titleInput = wrapper.find('input[name="title"]')
      const weightInput = wrapper.find('input[name="weight"]')

      await titleInput.setValue('Test Goal')
      await weightInput.setValue('23')
      await wrapper.find('form').trigger('submit')
      await nextTick()

      const errorMessage = wrapper.find('.error-message')
      expect(errorMessage.exists()).toBe(true)
      expect(errorMessage.text()).toContain('multiple of 5')
    })

    it('should show error when weight is below 5', async () => {
      const wrapper = createWrapper()

      const titleInput = wrapper.find('input[name="title"]')
      const weightInput = wrapper.find('input[name="weight"]')

      await titleInput.setValue('Test Goal')
      await weightInput.setValue('3')
      await wrapper.find('form').trigger('submit')
      await nextTick()

      const errorMessage = wrapper.find('.error-message')
      expect(errorMessage.exists()).toBe(true)
    })

    it('should show error when weight exceeds 100', async () => {
      const wrapper = createWrapper()

      const titleInput = wrapper.find('input[name="title"]')
      const weightInput = wrapper.find('input[name="weight"]')

      await titleInput.setValue('Test Goal')
      await weightInput.setValue('105')
      await wrapper.find('form').trigger('submit')
      await nextTick()

      const errorMessage = wrapper.find('.error-message')
      expect(errorMessage.exists()).toBe(true)
    })

    it('should clear validation errors when input changes', async () => {
      const wrapper = createWrapper()

      // Trigger validation error
      await wrapper.find('form').trigger('submit')
      await nextTick()
      expect(wrapper.find('.error-message').exists()).toBe(true)

      // Fix the error by typing in title
      const titleInput = wrapper.find('input[name="title"]')
      await titleInput.setValue('Valid Title')
      await nextTick()

      expect(wrapper.find('.error-message[data-field="title"]').exists()).toBe(false)
    })
  })

  describe('events', () => {
    it('should emit save event with form data on valid submit', async () => {
      const wrapper = createWrapper()

      const titleInput = wrapper.find('input[name="title"]')
      const descriptionTextarea = wrapper.find('textarea[name="description"]')
      const typeSelect = wrapper.find('select[name="goal_type"]')
      const weightInput = wrapper.find('input[name="weight"]')

      await titleInput.setValue('New Goal')
      await descriptionTextarea.setValue('Description')
      await typeSelect.setValue(GoalType.SCF)
      await weightInput.setValue('25')

      await wrapper.find('form').trigger('submit')
      await nextTick()

      const saveEvents = wrapper.emitted('save')
      expect(saveEvents).toBeTruthy()
      expect(saveEvents![0][0]).toEqual({
        title: 'New Goal',
        description: 'Description',
        goal_type: GoalType.SCF,
        weight: 25,
      })
    })

    it('should emit cancel event when cancel button clicked', async () => {
      const wrapper = createWrapper()

      const cancelButton = wrapper.find('.form-actions button.btn-secondary')
      await cancelButton.trigger('click')

      const cancelEvents = wrapper.emitted('cancel')
      expect(cancelEvents).toBeTruthy()
    })

    it('should not emit save event when validation fails', async () => {
      const wrapper = createWrapper()

      // Submit form with empty title
      await wrapper.find('form').trigger('submit')
      await nextTick()

      const saveEvents = wrapper.emitted('save')
      expect(saveEvents).toBeFalsy()
    })

    it('should emit save with updated data in edit mode', async () => {
      const existingGoal: Goal = {
        id: 'goal-1',
        review_id: 'review-123',
        title: 'Original Title',
        description: 'Original description',
        goal_type: GoalType.STANDARD,
        weight: 30,
        score: null,
        display_order: 0,
      }

      const wrapper = createWrapper({ goal: existingGoal })

      const titleInput = wrapper.find('input[name="title"]')
      await titleInput.setValue('Updated Title')

      await wrapper.find('form').trigger('submit')
      await nextTick()

      const saveEvents = wrapper.emitted('save')
      expect(saveEvents).toBeTruthy()
      expect(saveEvents![0][0]).toMatchObject({
        title: 'Updated Title',
        description: 'Original description',
        goal_type: GoalType.STANDARD,
        weight: 30,
      })
    })
  })

  describe('loading state', () => {
    it('should disable form fields when loading', () => {
      const wrapper = createWrapper({ loading: true })

      const titleInput = wrapper.find('input[name="title"]')
      const descriptionTextarea = wrapper.find('textarea[name="description"]')
      const typeSelect = wrapper.find('select[name="goal_type"]')
      const weightInput = wrapper.find('input[name="weight"]')
      const saveButton = wrapper.find('button[type="submit"]')

      expect((titleInput.element as HTMLInputElement).disabled).toBe(true)
      expect((descriptionTextarea.element as HTMLTextAreaElement).disabled).toBe(true)
      expect((typeSelect.element as HTMLSelectElement).disabled).toBe(true)
      expect((weightInput.element as HTMLInputElement).disabled).toBe(true)
      expect((saveButton.element as HTMLButtonElement).disabled).toBe(true)
    })

    it('should show loading text on save button when loading', () => {
      const wrapper = createWrapper({ loading: true })

      const saveButton = wrapper.find('button[type="submit"]')
      expect(saveButton.text()).toContain('Saving')
    })
  })

  describe('weight slider', () => {
    it('should update weight display when slider changes', async () => {
      const wrapper = createWrapper()

      const weightInput = wrapper.find('input[name="weight"]')
      await weightInput.setValue('45')
      await nextTick()

      const weightDisplay = wrapper.find('.weight-display')
      expect(weightDisplay.text()).toContain('45%')
    })

    it('should snap weight to nearest multiple of 5', async () => {
      const wrapper = createWrapper()

      const weightInput = wrapper.find('input[name="weight"]')
      await weightInput.setValue('47')
      await weightInput.trigger('blur')
      await nextTick()

      // Should snap to 45 or 50
      const value = parseInt((weightInput.element as HTMLInputElement).value)
      expect(value % 5).toBe(0)
    })
  })
})
