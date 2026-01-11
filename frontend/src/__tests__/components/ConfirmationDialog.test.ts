// TSS PPM v3.0 - ConfirmationDialog Component Tests
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ConfirmationDialog from '../../components/common/ConfirmationDialog.vue'

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

describe('ConfirmationDialog', () => {
  describe('dialog content', () => {
    it('should display dialog title', () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Confirm Action',
          message: 'Are you sure?',
        },
        global: globalStubs,
      })

      expect(wrapper.text()).toContain('Confirm Action')
    })

    it('should display dialog message', () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Confirm',
          message: 'This action cannot be undone.',
        },
        global: globalStubs,
      })

      expect(wrapper.text()).toContain('This action cannot be undone.')
    })

    it('should render cancel button', () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Confirm',
          message: 'Are you sure?',
        },
        global: globalStubs,
      })

      expect(wrapper.find('.cancel-button').exists()).toBe(true)
    })

    it('should render confirm button', () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Confirm',
          message: 'Are you sure?',
        },
        global: globalStubs,
      })

      expect(wrapper.find('.confirm-button').exists()).toBe(true)
    })

    it('should use custom confirm button text', () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Delete Item',
          message: 'Are you sure?',
          confirmText: 'Delete',
        },
        global: globalStubs,
      })

      expect(wrapper.find('.confirm-button').text()).toBe('Delete')
    })

    it('should use custom cancel button text', () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Delete Item',
          message: 'Are you sure?',
          cancelText: 'Go Back',
        },
        global: globalStubs,
      })

      expect(wrapper.find('.cancel-button').text()).toBe('Go Back')
    })
  })

  describe('visibility', () => {
    it('should not render when modelValue is false', () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: false,
          title: 'Confirm',
          message: 'Are you sure?',
        },
        global: globalStubs,
      })

      expect(wrapper.find('.dialog-overlay').exists()).toBe(false)
    })

    it('should render when modelValue is true', () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Confirm',
          message: 'Are you sure?',
        },
        global: globalStubs,
      })

      expect(wrapper.find('.dialog-overlay').exists()).toBe(true)
    })
  })

  describe('actions', () => {
    it('should emit update:modelValue false and cancel when cancel is clicked', async () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Confirm',
          message: 'Are you sure?',
        },
        global: globalStubs,
      })

      await wrapper.find('.cancel-button').trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
      expect(wrapper.emitted('cancel')).toBeTruthy()
    })

    it('should emit update:modelValue false and confirm when confirm is clicked', async () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Confirm',
          message: 'Are you sure?',
        },
        global: globalStubs,
      })

      await wrapper.find('.confirm-button').trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
      expect(wrapper.emitted('confirm')).toBeTruthy()
    })

    it('should close when backdrop is clicked', async () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Confirm',
          message: 'Are you sure?',
        },
        global: globalStubs,
      })

      await wrapper.find('.dialog-backdrop').trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
    })
  })

  describe('loading state', () => {
    it('should show loading spinner when loading is true', () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Confirm',
          message: 'Are you sure?',
          loading: true,
        },
        global: globalStubs,
      })

      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    })

    it('should disable confirm button when loading', () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Confirm',
          message: 'Are you sure?',
          loading: true,
        },
        global: globalStubs,
      })

      expect(wrapper.find('.confirm-button').attributes('disabled')).toBeDefined()
    })

    it('should disable cancel button when loading', () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Confirm',
          message: 'Are you sure?',
          loading: true,
        },
        global: globalStubs,
      })

      expect(wrapper.find('.cancel-button').attributes('disabled')).toBeDefined()
    })
  })

  describe('danger variant', () => {
    it('should apply danger styling when variant is danger', () => {
      const wrapper = mount(ConfirmationDialog, {
        props: {
          modelValue: true,
          title: 'Delete Item',
          message: 'This cannot be undone.',
          variant: 'danger',
        },
        global: globalStubs,
      })

      expect(wrapper.find('.confirm-button').classes()).toContain('danger')
    })
  })
})
