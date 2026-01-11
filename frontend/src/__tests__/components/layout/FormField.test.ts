// TSS PPM v3.0 - FormField Component Tests
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FormField from '../../../components/layout/FormField.vue'

describe('FormField', () => {
  function createWrapper(options = {}) {
    return mount(FormField, {
      props: {
        label: 'Field Label',
      },
      ...options,
    })
  }

  describe('label', () => {
    it('should render label text', () => {
      const wrapper = createWrapper({
        props: {
          label: 'Goal Name',
        },
      })
      expect(wrapper.text()).toContain('Goal Name')
    })

    it('should render label element', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('label').exists()).toBe(true)
    })

    it('should associate label with input via htmlFor', () => {
      const wrapper = createWrapper({
        props: {
          label: 'Test Label',
          id: 'test-field',
        },
      })
      const label = wrapper.find('label')
      expect(label.attributes('for')).toBe('test-field')
    })
  })

  describe('input slot', () => {
    it('should render slot content', () => {
      const wrapper = createWrapper({
        slots: {
          default: '<input type="text" id="test-input" />',
        },
      })
      expect(wrapper.find('#test-input').exists()).toBe(true)
    })

    it('should render complex slot content', () => {
      const wrapper = createWrapper({
        slots: {
          default: '<select id="goal-type"><option>Standard</option><option>KAR</option></select>',
        },
      })
      expect(wrapper.find('#goal-type').exists()).toBe(true)
    })
  })

  describe('required indicator', () => {
    it('should not show required asterisk by default', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.form-field__required').exists()).toBe(false)
    })

    it('should show required asterisk when required prop is true', () => {
      const wrapper = createWrapper({
        props: {
          label: 'Required Field',
          required: true,
        },
      })
      expect(wrapper.find('.form-field__required').exists()).toBe(true)
      expect(wrapper.text()).toContain('*')
    })
  })

  describe('voice input', () => {
    it('should not show voice input icon by default', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.form-field__voice').exists()).toBe(false)
    })

    it('should show voice input icon when voiceEnabled is true', () => {
      const wrapper = createWrapper({
        props: {
          label: 'Voice Field',
          voiceEnabled: true,
        },
      })
      expect(wrapper.find('.form-field__voice').exists()).toBe(true)
    })

    it('should emit voice-click event when voice icon clicked', async () => {
      const wrapper = createWrapper({
        props: {
          label: 'Voice Field',
          voiceEnabled: true,
        },
      })
      await wrapper.find('.form-field__voice').trigger('click')
      expect(wrapper.emitted('voice-click')).toBeTruthy()
    })
  })

  describe('error state', () => {
    it('should not show error message by default', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.form-field__error').exists()).toBe(false)
    })

    it('should show error message when error prop provided', () => {
      const wrapper = createWrapper({
        props: {
          label: 'Field',
          error: 'This field is required',
        },
      })
      expect(wrapper.find('.form-field__error').exists()).toBe(true)
      expect(wrapper.text()).toContain('This field is required')
    })

    it('should apply error styling class when error exists', () => {
      const wrapper = createWrapper({
        props: {
          label: 'Field',
          error: 'Error message',
        },
      })
      expect(wrapper.find('.form-field').classes()).toContain('form-field--error')
    })
  })

  describe('styling', () => {
    it('should have form-field root class', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.form-field').exists()).toBe(true)
    })

    it('should have form-field__label class on label', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.form-field__label').exists()).toBe(true)
    })

    it('should have form-field__input class on input wrapper', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.form-field__input').exists()).toBe(true)
    })
  })
})
