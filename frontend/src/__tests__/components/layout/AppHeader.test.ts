// TSS PPM v3.0 - AppHeader Component Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import AppHeader from '../../../components/layout/AppHeader.vue'

// Mock vue-i18n
const mockLocale = ref('en')
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'header.progress': 'Complete',
        'header.language': 'Language',
      }
      return messages[key] || key
    },
    locale: mockLocale,
  }),
}))

describe('AppHeader', () => {
  beforeEach(() => {
    mockLocale.value = 'en'
  })

  function createWrapper(props = {}) {
    return mount(AppHeader, {
      props: {
        progress: 0,
        ...props,
      },
    })
  }

  describe('progress bar', () => {
    it('should render progress bar', () => {
      const wrapper = createWrapper({ progress: 50 })
      expect(wrapper.find('.progress-bar').exists()).toBe(true)
    })

    it('should display progress percentage', () => {
      const wrapper = createWrapper({ progress: 25 })
      expect(wrapper.text()).toContain('25%')
    })

    it('should show 0% when progress is 0', () => {
      const wrapper = createWrapper({ progress: 0 })
      expect(wrapper.text()).toContain('0%')
    })

    it('should show 100% when progress is 100', () => {
      const wrapper = createWrapper({ progress: 100 })
      expect(wrapper.text()).toContain('100%')
    })

    it('should set progress bar width based on percentage', () => {
      const wrapper = createWrapper({ progress: 75 })
      const progressFill = wrapper.find('.progress-fill')
      expect(progressFill.attributes('style')).toContain('width: 75%')
    })
  })

  describe('language selector', () => {
    it('should render language selector with three options', () => {
      const wrapper = createWrapper()
      const langButtons = wrapper.findAll('.lang-btn')
      expect(langButtons.length).toBe(3)
    })

    it('should show EN, NL, and ES options', () => {
      const wrapper = createWrapper()
      const text = wrapper.text()
      expect(text).toContain('EN')
      expect(text).toContain('NL')
      expect(text).toContain('ES')
    })

    it('should highlight current locale button', () => {
      mockLocale.value = 'nl'
      const wrapper = createWrapper()
      const nlButton = wrapper.findAll('.lang-btn').find((btn) => btn.text().includes('NL'))
      expect(nlButton?.classes()).toContain('is-active')
    })

    it('should emit locale-change when language button clicked', async () => {
      const wrapper = createWrapper()
      const nlButton = wrapper.findAll('.lang-btn').find((btn) => btn.text().includes('NL'))
      await nlButton?.trigger('click')
      expect(wrapper.emitted('locale-change')).toBeTruthy()
      expect(wrapper.emitted('locale-change')?.[0]).toEqual(['nl'])
    })

    it('should change locale when language button clicked', async () => {
      const wrapper = createWrapper()
      const esButton = wrapper.findAll('.lang-btn').find((btn) => btn.text().includes('ES'))
      await esButton?.trigger('click')
      // The locale change should be handled by the component
      expect(mockLocale.value).toBe('es')
    })
  })

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
