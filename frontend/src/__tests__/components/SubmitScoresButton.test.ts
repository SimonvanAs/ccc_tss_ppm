// TSS PPM v3.0 - SubmitScoresButton Component Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import SubmitScoresButton from '../../components/review/SubmitScoresButton.vue'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
    locale: { value: 'en' },
  }),
}))

describe('SubmitScoresButton', () => {
  describe('disabled state when scores incomplete', () => {
    it('should be disabled when allScoresComplete is false', () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: false },
      })

      const button = wrapper.find('button')
      expect(button.attributes('disabled')).toBeDefined()
    })

    it('should show disabled styling when incomplete', () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: false },
      })

      const button = wrapper.find('button')
      expect(button.classes()).toContain('disabled')
    })

    it('should not open dialog when clicked while disabled', async () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: false },
      })

      await wrapper.find('button').trigger('click')

      expect(wrapper.find('.confirmation-dialog').exists()).toBe(false)
    })

    it('should show helpful tooltip when disabled', () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: false },
      })

      const button = wrapper.find('button')
      expect(button.attributes('title')).toContain('scores')
    })
  })

  describe('enabled state when all scores entered', () => {
    it('should be enabled when allScoresComplete is true', () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true },
      })

      const button = wrapper.find('button')
      expect(button.attributes('disabled')).toBeUndefined()
    })

    it('should show enabled styling when complete', () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true },
      })

      const button = wrapper.find('button')
      expect(button.classes()).not.toContain('disabled')
    })

    it('should display submit button text', () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true },
      })

      expect(wrapper.text()).toContain('Submit')
    })
  })

  describe('confirmation dialog display', () => {
    it('should open dialog when button is clicked', async () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true },
      })

      await wrapper.find('button.submit-button').trigger('click')

      expect(wrapper.find('.confirmation-dialog').exists()).toBe(true)
    })

    it('should show confirmation message in dialog', async () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true },
      })

      await wrapper.find('button.submit-button').trigger('click')

      expect(wrapper.text()).toContain('submit')
    })

    it('should show cancel button in dialog', async () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true },
      })

      await wrapper.find('button.submit-button').trigger('click')

      expect(wrapper.find('.cancel-button').exists()).toBe(true)
    })

    it('should show confirm button in dialog', async () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true },
      })

      await wrapper.find('button.submit-button').trigger('click')

      expect(wrapper.find('.confirm-button').exists()).toBe(true)
    })

    it('should close dialog when cancel is clicked', async () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true },
      })

      await wrapper.find('button.submit-button').trigger('click')
      await wrapper.find('.cancel-button').trigger('click')

      expect(wrapper.find('.confirmation-dialog').exists()).toBe(false)
    })
  })

  describe('API call on confirmation', () => {
    it('should emit submit event when confirm is clicked', async () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true },
      })

      await wrapper.find('button.submit-button').trigger('click')
      await wrapper.find('.confirm-button').trigger('click')

      expect(wrapper.emitted('submit')).toBeTruthy()
    })

    it('should show loading state while submitting', async () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true, isSubmitting: true },
      })

      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    })

    it('should disable button while submitting', async () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true, isSubmitting: true },
      })

      const button = wrapper.find('button.submit-button')
      expect(button.attributes('disabled')).toBeDefined()
    })

    it('should close dialog after submit event is emitted', async () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true },
      })

      await wrapper.find('button.submit-button').trigger('click')
      await wrapper.find('.confirm-button').trigger('click')

      expect(wrapper.find('.confirmation-dialog').exists()).toBe(false)
    })
  })

  describe('error handling', () => {
    it('should display error message when hasError is true', () => {
      const wrapper = mount(SubmitScoresButton, {
        props: { allScoresComplete: true, hasError: true, errorMessage: 'Submission failed' },
      })

      expect(wrapper.find('.error-message').exists()).toBe(true)
      expect(wrapper.text()).toContain('Submission failed')
    })
  })
})
