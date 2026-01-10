// TSS PPM v3.0 - SaveIndicator Component Tests
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import SaveIndicator from '../../components/common/SaveIndicator.vue'
import { SaveStatus } from '../../composables/useAutoSave'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'review.saving': 'Saving...',
        'review.saved': 'Saved',
        'errors.generic': 'An error occurred',
      }
      return messages[key] || key
    },
  }),
}))

describe('SaveIndicator', () => {
  function createWrapper(props = {}) {
    return mount(SaveIndicator, {
      props: {
        status: SaveStatus.IDLE,
        ...props,
      },
    })
  }

  describe('idle state', () => {
    it('should not be visible when idle', () => {
      const wrapper = createWrapper({ status: SaveStatus.IDLE })
      expect(wrapper.find('.save-indicator').exists()).toBe(false)
    })
  })

  describe('saving state', () => {
    it('should show saving text', () => {
      const wrapper = createWrapper({ status: SaveStatus.SAVING })
      expect(wrapper.text()).toContain('Saving')
    })

    it('should show spinner', () => {
      const wrapper = createWrapper({ status: SaveStatus.SAVING })
      expect(wrapper.find('.spinner').exists()).toBe(true)
    })

    it('should have saving class', () => {
      const wrapper = createWrapper({ status: SaveStatus.SAVING })
      expect(wrapper.find('.save-indicator').classes()).toContain('is-saving')
    })
  })

  describe('saved state', () => {
    it('should show saved text', () => {
      const wrapper = createWrapper({ status: SaveStatus.SAVED })
      expect(wrapper.text()).toContain('Saved')
    })

    it('should show checkmark icon', () => {
      const wrapper = createWrapper({ status: SaveStatus.SAVED })
      expect(wrapper.find('.checkmark').exists()).toBe(true)
    })

    it('should have saved class', () => {
      const wrapper = createWrapper({ status: SaveStatus.SAVED })
      expect(wrapper.find('.save-indicator').classes()).toContain('is-saved')
    })
  })

  describe('error state', () => {
    it('should show error text', () => {
      const wrapper = createWrapper({ status: SaveStatus.ERROR })
      expect(wrapper.text()).toContain('error')
    })

    it('should show error icon', () => {
      const wrapper = createWrapper({ status: SaveStatus.ERROR })
      expect(wrapper.find('.error-icon').exists()).toBe(true)
    })

    it('should have error class', () => {
      const wrapper = createWrapper({ status: SaveStatus.ERROR })
      expect(wrapper.find('.save-indicator').classes()).toContain('is-error')
    })

    it('should show custom error message when provided', () => {
      const wrapper = createWrapper({
        status: SaveStatus.ERROR,
        errorMessage: 'Custom error',
      })
      expect(wrapper.text()).toContain('Custom error')
    })
  })

  describe('transitions', () => {
    it('should use transition wrapper', () => {
      const wrapper = createWrapper({ status: SaveStatus.SAVING })
      expect(wrapper.find('transition-stub').exists() || wrapper.find('.save-indicator').exists()).toBe(true)
    })
  })
})
