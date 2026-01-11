// TSS PPM v3.0 - SectionHeader Component Tests
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SectionHeader from '../../../components/layout/SectionHeader.vue'

describe('SectionHeader', () => {
  function createWrapper(options = {}) {
    return mount(SectionHeader, {
      props: {
        title: 'Test Title',
      },
      ...options,
    })
  }

  describe('title', () => {
    it('should render title text', () => {
      const wrapper = createWrapper({
        props: {
          title: 'Goals Overview',
        },
      })
      expect(wrapper.text()).toContain('Goals Overview')
    })

    it('should render title in h2 element', () => {
      const wrapper = createWrapper({
        props: {
          title: 'Section Title',
        },
      })
      const heading = wrapper.find('h2')
      expect(heading.exists()).toBe(true)
      expect(heading.text()).toContain('Section Title')
    })
  })

  describe('styling', () => {
    it('should have section-header root class', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.section-header').exists()).toBe(true)
    })

    it('should have section-header__title class on title element', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.section-header__title').exists()).toBe(true)
    })
  })

  describe('subtitle', () => {
    it('should not render subtitle when not provided', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.section-header__subtitle').exists()).toBe(false)
    })

    it('should render subtitle slot content when provided', () => {
      const wrapper = createWrapper({
        slots: {
          subtitle: '<span>Optional description text</span>',
        },
      })
      expect(wrapper.find('.section-header__subtitle').exists()).toBe(true)
      expect(wrapper.text()).toContain('Optional description text')
    })

    it('should render subtitle prop when provided', () => {
      const wrapper = createWrapper({
        props: {
          title: 'Main Title',
          subtitle: 'Subtitle text here',
        },
      })
      expect(wrapper.text()).toContain('Subtitle text here')
    })

    it('should prefer slot over subtitle prop', () => {
      const wrapper = createWrapper({
        props: {
          title: 'Main Title',
          subtitle: 'Prop subtitle',
        },
        slots: {
          subtitle: '<span>Slot subtitle</span>',
        },
      })
      expect(wrapper.text()).toContain('Slot subtitle')
    })
  })

  describe('actions slot', () => {
    it('should not render actions area when slot not provided', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.section-header__actions').exists()).toBe(false)
    })

    it('should render actions slot when provided', () => {
      const wrapper = createWrapper({
        slots: {
          actions: '<button>Add New</button>',
        },
      })
      expect(wrapper.find('.section-header__actions').exists()).toBe(true)
      expect(wrapper.text()).toContain('Add New')
    })
  })
})
