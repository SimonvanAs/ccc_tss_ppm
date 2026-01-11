// TSS PPM v3.0 - SignatureModal Component Tests
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import SignatureModal from '../../components/review/SignatureModal.vue'

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

describe('SignatureModal', () => {
  const defaultProps = {
    modelValue: true,
    reviewSummary: {
      employeeName: 'John Doe',
      stage: 'END_YEAR_REVIEW',
      whatScore: 2.5,
      howScore: 2.0,
    },
  }

  describe('rendering', () => {
    it('should display modal when modelValue is true', () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.find('.signature-modal').exists()).toBe(true)
    })

    it('should not display modal when modelValue is false', () => {
      const wrapper = mount(SignatureModal, {
        props: { ...defaultProps, modelValue: false },
        global: globalStubs,
      })

      expect(wrapper.find('.signature-modal').exists()).toBe(false)
    })

    it('should display review summary information', () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.text()).toContain('John Doe')
    })

    it('should display WHAT score', () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.text()).toContain('2.5')
    })

    it('should display HOW score', () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.text()).toContain('2.0')
    })
  })

  describe('checkbox acknowledgment', () => {
    it('should render checkbox for acknowledgment', () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.find('input[type="checkbox"]').exists()).toBe(true)
    })

    it('should have checkbox unchecked by default', () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      const checkbox = wrapper.find('input[type="checkbox"]')
      expect((checkbox.element as HTMLInputElement).checked).toBe(false)
    })

    it('should display acknowledgment text', () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      // Should contain something like "I have reviewed and agree"
      expect(wrapper.text()).toMatch(/review|agree/i)
    })
  })

  describe('sign button', () => {
    it('should render Sign Review button', () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.find('.sign-button').exists()).toBe(true)
    })

    it('should have Sign Review button disabled when checkbox is unchecked', () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      const signButton = wrapper.find('.sign-button')
      expect(signButton.attributes('disabled')).toBeDefined()
    })

    it('should enable Sign Review button when checkbox is checked', async () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)

      const signButton = wrapper.find('.sign-button')
      expect(signButton.attributes('disabled')).toBeUndefined()
    })

    it('should emit sign event when Sign Review button is clicked', async () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      // Check the checkbox first
      const checkbox = wrapper.find('input[type="checkbox"]')
      await checkbox.setValue(true)

      // Click sign button
      await wrapper.find('.sign-button').trigger('click')

      expect(wrapper.emitted('sign')).toBeTruthy()
    })
  })

  describe('cancel button', () => {
    it('should render Cancel button', () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.find('.cancel-button').exists()).toBe(true)
    })

    it('should emit update:modelValue false when Cancel is clicked', async () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      await wrapper.find('.cancel-button').trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
    })
  })

  describe('loading state', () => {
    it('should disable buttons when loading', () => {
      const wrapper = mount(SignatureModal, {
        props: { ...defaultProps, loading: true },
        global: globalStubs,
      })

      expect(wrapper.find('.sign-button').attributes('disabled')).toBeDefined()
      expect(wrapper.find('.cancel-button').attributes('disabled')).toBeDefined()
    })

    it('should show loading indicator when loading', () => {
      const wrapper = mount(SignatureModal, {
        props: { ...defaultProps, loading: true },
        global: globalStubs,
      })

      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    })
  })

  describe('styling', () => {
    it('should use brand magenta color for sign button', () => {
      const wrapper = mount(SignatureModal, {
        props: defaultProps,
        global: globalStubs,
      })

      expect(wrapper.find('.sign-button').classes()).toContain('primary')
    })
  })
})
