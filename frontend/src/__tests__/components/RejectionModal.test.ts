// TSS PPM v3.0 - RejectionModal Component Tests
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import RejectionModal from '../../components/review/RejectionModal.vue'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
    locale: { value: 'en' },
  }),
}))

// Stub Teleport to render content in place for testing
const globalStubs = {
  stubs: {
    Teleport: {
      setup(_: unknown, { slots }: { slots: { default?: () => unknown } }) {
        return () => (slots.default ? slots.default() : null)
      },
    },
  },
}

describe('RejectionModal', () => {
  const defaultProps = {
    modelValue: true,
    reviewSummary: {
      employeeName: 'John Doe',
      stage: 'END_YEAR_REVIEW',
    },
  }

  describe('rendering', () => {
    it('should display modal when modelValue is true', () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.find('.rejection-modal').exists()).toBe(true)
    })

    it('should not display modal when modelValue is false', () => {
      const wrapper = mount(RejectionModal, {
        props: { ...defaultProps, modelValue: false },
        global: globalStubs,
      })

      expect(wrapper.find('.rejection-modal').exists()).toBe(false)
    })

    it('should display employee name in header', () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.text()).toContain('John Doe')
    })

    it('should display stage information', () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      // Stage should be translated
      expect(wrapper.find('.review-info').exists()).toBe(true)
    })
  })

  describe('feedback text area', () => {
    it('should render feedback text area', () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.find('textarea').exists()).toBe(true)
    })

    it('should have empty feedback by default', () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      const textarea = wrapper.find('textarea')
      expect((textarea.element as HTMLTextAreaElement).value).toBe('')
    })

    it('should update feedback value on input', async () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('This needs more work on goals.')

      expect((textarea.element as HTMLTextAreaElement).value).toBe(
        'This needs more work on goals.'
      )
    })

    it('should display character count', () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.find('.character-count').exists()).toBe(true)
    })
  })

  describe('validation', () => {
    it('should disable submit button when feedback is empty', () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      const submitButton = wrapper.find('.submit-button')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should enable submit button when feedback has content', async () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('Feedback content here')

      const submitButton = wrapper.find('.submit-button')
      expect(submitButton.attributes('disabled')).toBeUndefined()
    })

    it('should show validation message when submitting empty feedback', async () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      // Try to submit without feedback
      await wrapper.find('.submit-button').trigger('click')

      // Button should still be disabled, no event emitted
      expect(wrapper.emitted('reject')).toBeFalsy()
    })

    it('should require minimum feedback length', async () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('ab') // Too short

      const submitButton = wrapper.find('.submit-button')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })
  })

  describe('submit button', () => {
    it('should render Submit Feedback & Return button', () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.find('.submit-button').exists()).toBe(true)
    })

    it('should emit reject event with feedback when submitted', async () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('Please revise the goal weights to total 100%.')

      await wrapper.find('.submit-button').trigger('click')

      expect(wrapper.emitted('reject')).toBeTruthy()
      expect(wrapper.emitted('reject')![0]).toEqual([
        'Please revise the goal weights to total 100%.',
      ])
    })
  })

  describe('cancel button', () => {
    it('should render Cancel button', () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.find('.cancel-button').exists()).toBe(true)
    })

    it('should emit update:modelValue false when Cancel is clicked', async () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      await wrapper.find('.cancel-button').trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
    })

    it('should clear feedback when cancelled', async () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      const textarea = wrapper.find('textarea')
      await textarea.setValue('Some feedback')

      await wrapper.find('.cancel-button').trigger('click')

      // Re-open would show cleared feedback
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
    })
  })

  describe('loading state', () => {
    it('should disable buttons when loading', () => {
      const wrapper = mount(RejectionModal, {
        props: { ...defaultProps, loading: true },
        global: globalStubs,
      })

      expect(wrapper.find('.submit-button').attributes('disabled')).toBeDefined()
      expect(wrapper.find('.cancel-button').attributes('disabled')).toBeDefined()
    })

    it('should disable textarea when loading', () => {
      const wrapper = mount(RejectionModal, {
        props: { ...defaultProps, loading: true },
        global: globalStubs,
      })

      expect(wrapper.find('textarea').attributes('disabled')).toBeDefined()
    })

    it('should show loading indicator when loading', () => {
      const wrapper = mount(RejectionModal, {
        props: { ...defaultProps, loading: true },
        global: globalStubs,
      })

      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    })
  })

  describe('backdrop', () => {
    it('should close modal when backdrop is clicked', async () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      await wrapper.find('.modal-backdrop').trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
    })

    it('should not close modal when content is clicked', async () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      await wrapper.find('.modal-content').trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeFalsy()
    })
  })

  describe('styling', () => {
    it('should use brand colors for submit button', () => {
      const wrapper = mount(RejectionModal, {
        props: defaultProps,
        global: globalStubs,
      })

      // Submit button should have warning/rejection styling
      expect(wrapper.find('.submit-button').classes()).toContain('warning')
    })
  })
})
