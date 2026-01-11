// TSS PPM v3.0 - AppHeader Component Tests
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AppHeader from '../../../components/layout/AppHeader.vue'

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
})
