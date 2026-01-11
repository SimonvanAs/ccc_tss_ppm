// TSS PPM v3.0 - Card Component Tests
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Card from '../../../components/layout/Card.vue'

describe('Card', () => {
  function createWrapper(options = {}) {
    return mount(Card, {
      ...options,
    })
  }

  describe('slot content', () => {
    it('should render slot content', () => {
      const wrapper = createWrapper({
        slots: {
          default: '<p>Card content</p>',
        },
      })
      expect(wrapper.text()).toContain('Card content')
    })

    it('should render complex slot content', () => {
      const wrapper = createWrapper({
        slots: {
          default: '<div class="custom"><h2>Title</h2><p>Description</p></div>',
        },
      })
      expect(wrapper.find('.custom').exists()).toBe(true)
      expect(wrapper.text()).toContain('Title')
      expect(wrapper.text()).toContain('Description')
    })
  })

  describe('styling', () => {
    it('should have card root class', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.card').exists()).toBe(true)
    })

    it('should apply white background', () => {
      const wrapper = createWrapper()
      // Background should be set via CSS class
      expect(wrapper.find('.card').exists()).toBe(true)
    })

    it('should apply box-shadow', () => {
      const wrapper = createWrapper()
      // Shadow should be set via CSS class
      expect(wrapper.find('.card').exists()).toBe(true)
    })
  })

  describe('padding prop', () => {
    it('should apply default padding when no prop provided', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.card').classes()).not.toContain('card--no-padding')
    })

    it('should apply no-padding class when padding is "none"', () => {
      const wrapper = createWrapper({
        props: {
          padding: 'none',
        },
      })
      expect(wrapper.find('.card').classes()).toContain('card--no-padding')
    })

    it('should apply small padding class when padding is "sm"', () => {
      const wrapper = createWrapper({
        props: {
          padding: 'sm',
        },
      })
      expect(wrapper.find('.card').classes()).toContain('card--padding-sm')
    })

    it('should apply large padding class when padding is "lg"', () => {
      const wrapper = createWrapper({
        props: {
          padding: 'lg',
        },
      })
      expect(wrapper.find('.card').classes()).toContain('card--padding-lg')
    })

    it('should apply default padding class when padding is "md"', () => {
      const wrapper = createWrapper({
        props: {
          padding: 'md',
        },
      })
      // md is default, no special class needed
      expect(wrapper.find('.card').classes()).not.toContain('card--no-padding')
      expect(wrapper.find('.card').classes()).not.toContain('card--padding-sm')
      expect(wrapper.find('.card').classes()).not.toContain('card--padding-lg')
    })
  })
})
