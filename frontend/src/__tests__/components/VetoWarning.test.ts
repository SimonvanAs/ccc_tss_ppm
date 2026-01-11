// TSS PPM v3.0 - VetoWarning Component Tests
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import VetoWarning from '../../components/review/VetoWarning.vue'

describe('VetoWarning', () => {
  describe('no veto', () => {
    it('should not render when no veto is active', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: null,
        },
      })

      expect(wrapper.find('.veto-warning').exists()).toBe(false)
    })

    it('should not render when vetoActive is false', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: null,
          vetoActive: false,
        },
      })

      expect(wrapper.find('.veto-warning').exists()).toBe(false)
    })
  })

  describe('SCF VETO warning', () => {
    it('should render SCF VETO warning', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'SCF',
          vetoActive: true,
        },
      })

      expect(wrapper.find('.veto-warning').exists()).toBe(true)
      expect(wrapper.find('.veto-warning').classes()).toContain('scf-veto')
    })

    it('should display SCF VETO title', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'SCF',
          vetoActive: true,
        },
      })

      expect(wrapper.text()).toContain('SCF VETO')
    })

    it('should display SCF VETO explanation', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'SCF',
          vetoActive: true,
        },
      })

      expect(wrapper.text()).toContain('Score reduced to 1.00')
    })

    it('should display warning icon', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'SCF',
          vetoActive: true,
        },
      })

      expect(wrapper.find('.veto-icon').exists()).toBe(true)
    })

    it('should display triggering goal name when provided', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'SCF',
          vetoActive: true,
          goalName: 'Safety Compliance',
        },
      })

      expect(wrapper.text()).toContain('Safety Compliance')
    })
  })

  describe('KAR VETO warning', () => {
    it('should render KAR VETO warning', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'KAR',
          vetoActive: true,
        },
      })

      expect(wrapper.find('.veto-warning').exists()).toBe(true)
      expect(wrapper.find('.veto-warning').classes()).toContain('kar-veto')
    })

    it('should display KAR VETO title', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'KAR',
          vetoActive: true,
        },
      })

      expect(wrapper.text()).toContain('KAR VETO')
    })

    it('should display KAR VETO explanation', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'KAR',
          vetoActive: true,
        },
      })

      expect(wrapper.text()).toContain('Score reduced to 1.00')
    })

    it('should indicate compensation is possible', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'KAR',
          vetoActive: true,
          showCompensationHint: true,
        },
      })

      expect(wrapper.text()).toContain('compensation')
    })

    it('should display compensated indicator when veto is compensated', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'KAR',
          vetoActive: false,
          compensated: true,
        },
      })

      expect(wrapper.find('.veto-compensated').exists()).toBe(true)
      expect(wrapper.text()).toContain('Compensated')
    })

    it('should display compensating goal name', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'KAR',
          vetoActive: false,
          compensated: true,
          compensatingGoalName: 'Key Account Revenue',
        },
      })

      expect(wrapper.text()).toContain('Key Account Revenue')
    })
  })

  describe('Competency VETO warning', () => {
    it('should render Competency VETO warning', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'COMPETENCY',
          vetoActive: true,
        },
      })

      expect(wrapper.find('.veto-warning').exists()).toBe(true)
      expect(wrapper.find('.veto-warning').classes()).toContain('competency-veto')
    })

    it('should display Competency VETO title', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'COMPETENCY',
          vetoActive: true,
        },
      })

      expect(wrapper.text()).toContain('Competency VETO')
    })

    it('should display triggering competency name', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'COMPETENCY',
          vetoActive: true,
          competencyName: 'Customer Focused',
        },
      })

      expect(wrapper.text()).toContain('Customer Focused')
    })
  })

  describe('styling', () => {
    it('should have danger styling for active veto', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'SCF',
          vetoActive: true,
        },
      })

      expect(wrapper.find('.veto-warning').classes()).toContain('veto-active')
    })

    it('should have success styling for compensated veto', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'KAR',
          vetoActive: false,
          compensated: true,
        },
      })

      expect(wrapper.find('.veto-compensated').classes()).toContain('veto-success')
    })
  })

  describe('accessibility', () => {
    it('should have role="alert" for active veto', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'SCF',
          vetoActive: true,
        },
      })

      expect(wrapper.find('.veto-warning').attributes('role')).toBe('alert')
    })

    it('should have aria-live="polite" for updates', () => {
      const wrapper = mount(VetoWarning, {
        props: {
          vetoType: 'SCF',
          vetoActive: true,
        },
      })

      expect(wrapper.find('.veto-warning').attributes('aria-live')).toBe('polite')
    })
  })
})
