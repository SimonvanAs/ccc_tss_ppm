// TSS PPM v3.0 - AppHeader Component Tests
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AppHeader from '../../../components/layout/AppHeader.vue'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'layout.header.ariaLabel': 'Application header',
        'layout.header.toggleSidebar': 'Toggle sidebar menu',
      }
      return messages[key] || key
    },
  }),
}))

describe('AppHeader', () => {
  function createWrapper(props = {}) {
    return mount(AppHeader, {
      props: {
        ...props,
      },
    })
  }

  describe('branding', () => {
    it('should display TSS PPM branding', () => {
      const wrapper = createWrapper()
      expect(wrapper.text()).toContain('TSS PPM')
    })

    it('should have app-header root class', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.app-header').exists()).toBe(true)
    })
  })

  describe('hamburger menu', () => {
    it('should render hamburger button when showHamburger prop is true', () => {
      const wrapper = createWrapper({ showHamburger: true })
      expect(wrapper.find('.hamburger-btn').exists()).toBe(true)
    })

    it('should not render hamburger button by default', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.hamburger-btn').exists()).toBe(false)
    })

    it('should emit toggle-sidebar when hamburger clicked', async () => {
      const wrapper = createWrapper({ showHamburger: true })
      await wrapper.find('.hamburger-btn').trigger('click')
      expect(wrapper.emitted('toggle-sidebar')).toBeTruthy()
    })
  })

  describe('accessibility', () => {
    it('should have aria-label on header', () => {
      const wrapper = createWrapper()
      const header = wrapper.find('.app-header')
      expect(header.attributes('aria-label')).toBe('Application header')
    })

    it('should have aria-label on hamburger button', () => {
      const wrapper = createWrapper({ showHamburger: true })
      const btn = wrapper.find('.hamburger-btn')
      expect(btn.attributes('aria-label')).toBe('Toggle sidebar menu')
    })
  })
})
