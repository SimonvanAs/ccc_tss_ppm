// TSS PPM v3.0 - ScoreSummary Component Tests
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ScoreSummary from '../../components/review/ScoreSummary.vue'

describe('ScoreSummary', () => {
  describe('WHAT score display', () => {
    it('should display WHAT score label', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.5, howScore: 2.0 },
      })

      expect(wrapper.text()).toContain('WHAT')
    })

    it('should display WHAT score value', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.5, howScore: 2.0 },
      })

      expect(wrapper.find('.what-score .score-value').text()).toBe('2.50')
    })

    it('should display WHAT score with 2 decimal places', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2, howScore: 2.0 },
      })

      expect(wrapper.find('.what-score .score-value').text()).toBe('2.00')
    })

    it('should display dash when WHAT score is null', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: null, howScore: 2.0 },
      })

      expect(wrapper.find('.what-score .score-value').text()).toBe('-')
    })

    it('should apply danger class when WHAT score is 1', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 1, howScore: 2.0 },
      })

      expect(wrapper.find('.what-score').classes()).toContain('score-danger')
    })

    it('should apply warning class when WHAT score is between 1 and 2', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 1.5, howScore: 2.0 },
      })

      expect(wrapper.find('.what-score').classes()).toContain('score-warning')
    })

    it('should apply success class when WHAT score is 2 or above', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.5, howScore: 2.0 },
      })

      expect(wrapper.find('.what-score').classes()).toContain('score-success')
    })
  })

  describe('HOW score display', () => {
    it('should display HOW score label', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.0, howScore: 2.5 },
      })

      expect(wrapper.text()).toContain('HOW')
    })

    it('should display HOW score value', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.0, howScore: 2.5 },
      })

      expect(wrapper.find('.how-score .score-value').text()).toBe('2.50')
    })

    it('should display HOW score with 2 decimal places', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.0, howScore: 3 },
      })

      expect(wrapper.find('.how-score .score-value').text()).toBe('3.00')
    })

    it('should display dash when HOW score is null', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.0, howScore: null },
      })

      expect(wrapper.find('.how-score .score-value').text()).toBe('-')
    })

    it('should apply danger class when HOW score is 1', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.0, howScore: 1 },
      })

      expect(wrapper.find('.how-score').classes()).toContain('score-danger')
    })

    it('should apply warning class when HOW score is between 1 and 2', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.0, howScore: 1.8 },
      })

      expect(wrapper.find('.how-score').classes()).toContain('score-warning')
    })

    it('should apply success class when HOW score is 2 or above', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.0, howScore: 2.5 },
      })

      expect(wrapper.find('.how-score').classes()).toContain('score-success')
    })
  })

  describe('VETO indicator integration', () => {
    it('should show SCF VETO indicator when SCF veto is active', () => {
      const wrapper = mount(ScoreSummary, {
        props: {
          whatScore: 1,
          howScore: 2.0,
          whatVetoActive: true,
          whatVetoType: 'SCF',
        },
      })

      expect(wrapper.find('.veto-badge').exists()).toBe(true)
      expect(wrapper.find('.veto-badge').text()).toContain('SCF')
    })

    it('should show KAR VETO indicator when KAR veto is active', () => {
      const wrapper = mount(ScoreSummary, {
        props: {
          whatScore: 1,
          howScore: 2.0,
          whatVetoActive: true,
          whatVetoType: 'KAR',
        },
      })

      expect(wrapper.find('.veto-badge').text()).toContain('KAR')
    })

    it('should show Competency VETO indicator when competency veto is active', () => {
      const wrapper = mount(ScoreSummary, {
        props: {
          whatScore: 2.0,
          howScore: 1,
          howVetoActive: true,
        },
      })

      expect(wrapper.find('.how-score .veto-badge').exists()).toBe(true)
    })

    it('should not show VETO indicator when no veto is active', () => {
      const wrapper = mount(ScoreSummary, {
        props: {
          whatScore: 2.5,
          howScore: 2.5,
          whatVetoActive: false,
          howVetoActive: false,
        },
      })

      expect(wrapper.find('.veto-badge').exists()).toBe(false)
    })

    it('should show VETO badge on WHAT score when WHAT veto is active', () => {
      const wrapper = mount(ScoreSummary, {
        props: {
          whatScore: 1,
          howScore: 2.5,
          whatVetoActive: true,
          whatVetoType: 'SCF',
        },
      })

      expect(wrapper.find('.what-score .veto-badge').exists()).toBe(true)
      expect(wrapper.find('.how-score .veto-badge').exists()).toBe(false)
    })

    it('should show VETO badge on HOW score when HOW veto is active', () => {
      const wrapper = mount(ScoreSummary, {
        props: {
          whatScore: 2.5,
          howScore: 1,
          howVetoActive: true,
        },
      })

      expect(wrapper.find('.how-score .veto-badge').exists()).toBe(true)
      expect(wrapper.find('.what-score .veto-badge').exists()).toBe(false)
    })
  })

  describe('layout', () => {
    it('should render both scores side by side', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.5, howScore: 2.5 },
      })

      expect(wrapper.find('.score-summary').exists()).toBe(true)
      expect(wrapper.find('.what-score').exists()).toBe(true)
      expect(wrapper.find('.how-score').exists()).toBe(true)
    })

    it('should apply compact class when compact prop is true', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.5, howScore: 2.5, compact: true },
      })

      expect(wrapper.find('.score-summary').classes()).toContain('compact')
    })
  })

  describe('accessibility', () => {
    it('should have appropriate aria-labels for scores', () => {
      const wrapper = mount(ScoreSummary, {
        props: { whatScore: 2.5, howScore: 2.3 },
      })

      const whatScore = wrapper.find('.what-score')
      const howScore = wrapper.find('.how-score')

      expect(whatScore.attributes('aria-label')).toContain('WHAT score')
      expect(howScore.attributes('aria-label')).toContain('HOW score')
    })
  })
})
