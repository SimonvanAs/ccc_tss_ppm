// TSS PPM v3.0 - CompetencyScoreCard Component Tests
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CompetencyScoreCard from '../../components/review/CompetencyScoreCard.vue'

describe('CompetencyScoreCard', () => {
  describe('renders three score buttons (1, 2, 3)', () => {
    it('should render three score options', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: { competencyId: 'comp-1' },
      })

      const buttons = wrapper.findAll('.score-button')
      expect(buttons).toHaveLength(3)
    })

    it('should display score numbers 1, 2, 3', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: { competencyId: 'comp-1' },
      })

      const buttons = wrapper.findAll('.score-button')
      expect(buttons[0].text()).toContain('1')
      expect(buttons[1].text()).toContain('2')
      expect(buttons[2].text()).toContain('3')
    })

    it('should render with custom labels when provided', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: {
          competencyId: 'comp-1',
          labels: {
            1: 'Below',
            2: 'Meets',
            3: 'Exceeds',
          },
        },
      })

      const buttons = wrapper.findAll('.score-button')
      expect(buttons[0].text()).toContain('Below')
      expect(buttons[1].text()).toContain('Meets')
      expect(buttons[2].text()).toContain('Exceeds')
    })
  })

  describe('selected state visual feedback', () => {
    it('should show no selection when modelValue is null', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: {
          competencyId: 'comp-1',
          modelValue: null,
        },
      })

      const selectedButtons = wrapper.findAll('.score-button.selected')
      expect(selectedButtons).toHaveLength(0)
    })

    it('should highlight selected score with magenta styling', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: {
          competencyId: 'comp-1',
          modelValue: 2,
        },
      })

      const buttons = wrapper.findAll('.score-button')
      expect(buttons[1].classes()).toContain('selected')
    })

    it('should apply score-1 class for potential VETO styling', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: {
          competencyId: 'comp-1',
          modelValue: 1,
        },
      })

      const buttons = wrapper.findAll('.score-button')
      expect(buttons[0].classes()).toContain('selected')
      expect(buttons[0].classes()).toContain('score-1')
    })

    it('should update selection when modelValue changes', async () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: {
          competencyId: 'comp-1',
          modelValue: 1,
        },
      })

      expect(wrapper.findAll('.score-button')[0].classes()).toContain('selected')

      await wrapper.setProps({ modelValue: 3 })

      const buttons = wrapper.findAll('.score-button')
      expect(buttons[0].classes()).not.toContain('selected')
      expect(buttons[2].classes()).toContain('selected')
    })
  })

  describe('click emits score-change event', () => {
    it('should emit score-change with competencyId and score when clicking', async () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: { competencyId: 'comp-1' },
      })

      const buttons = wrapper.findAll('.score-button')
      await buttons[1].trigger('click')

      expect(wrapper.emitted('score-change')).toBeTruthy()
      expect(wrapper.emitted('score-change')![0]).toEqual([
        { competencyId: 'comp-1', score: 2 },
      ])
    })

    it('should emit update:modelValue for v-model support', async () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: { competencyId: 'comp-1' },
      })

      const buttons = wrapper.findAll('.score-button')
      await buttons[2].trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([3])
    })

    it('should emit correct score for each button', async () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: { competencyId: 'comp-1' },
      })

      const buttons = wrapper.findAll('.score-button')

      await buttons[0].trigger('click')
      expect(wrapper.emitted('score-change')![0]).toEqual([
        { competencyId: 'comp-1', score: 1 },
      ])

      await buttons[1].trigger('click')
      expect(wrapper.emitted('score-change')![1]).toEqual([
        { competencyId: 'comp-1', score: 2 },
      ])

      await buttons[2].trigger('click')
      expect(wrapper.emitted('score-change')![2]).toEqual([
        { competencyId: 'comp-1', score: 3 },
      ])
    })
  })

  describe('disabled state', () => {
    it('should apply disabled class when disabled prop is true', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: {
          competencyId: 'comp-1',
          disabled: true,
        },
      })

      expect(wrapper.find('.competency-score-card').classes()).toContain('disabled')
    })

    it('should not emit events when disabled', async () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: {
          competencyId: 'comp-1',
          disabled: true,
        },
      })

      const buttons = wrapper.findAll('.score-button')
      await buttons[1].trigger('click')

      expect(wrapper.emitted('score-change')).toBeFalsy()
      expect(wrapper.emitted('update:modelValue')).toBeFalsy()
    })

    it('should show selection even when disabled', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: {
          competencyId: 'comp-1',
          modelValue: 2,
          disabled: true,
        },
      })

      const buttons = wrapper.findAll('.score-button')
      expect(buttons[1].classes()).toContain('selected')
    })
  })

  describe('VETO warning indicator', () => {
    it('should show VETO indicator when score is 1 and showVetoWarning is true', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: {
          competencyId: 'comp-1',
          modelValue: 1,
          showVetoWarning: true,
        },
      })

      expect(wrapper.find('.veto-indicator').exists()).toBe(true)
    })

    it('should not show VETO indicator when score is not 1', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: {
          competencyId: 'comp-1',
          modelValue: 2,
          showVetoWarning: true,
        },
      })

      expect(wrapper.find('.veto-indicator').exists()).toBe(false)
    })

    it('should not show VETO indicator when showVetoWarning is false', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: {
          competencyId: 'comp-1',
          modelValue: 1,
          showVetoWarning: false,
        },
      })

      expect(wrapper.find('.veto-indicator').exists()).toBe(false)
    })
  })

  describe('accessibility', () => {
    it('should have role="radiogroup"', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: { competencyId: 'comp-1' },
      })

      expect(wrapper.find('.competency-score-card').attributes('role')).toBe('radiogroup')
    })

    it('should have role="radio" for each button', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: { competencyId: 'comp-1' },
      })

      const buttons = wrapper.findAll('.score-button')
      buttons.forEach((button) => {
        expect(button.attributes('role')).toBe('radio')
      })
    })

    it('should have aria-checked for selected option', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: {
          competencyId: 'comp-1',
          modelValue: 2,
        },
      })

      const buttons = wrapper.findAll('.score-button')
      expect(buttons[0].attributes('aria-checked')).toBe('false')
      expect(buttons[1].attributes('aria-checked')).toBe('true')
      expect(buttons[2].attributes('aria-checked')).toBe('false')
    })

    it('should be keyboard accessible with tabindex', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: { competencyId: 'comp-1' },
      })

      const buttons = wrapper.findAll('.score-button')
      buttons.forEach((button) => {
        expect(button.attributes('tabindex')).toBe('0')
      })
    })

    it('should handle Enter key press', async () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: { competencyId: 'comp-1' },
      })

      const buttons = wrapper.findAll('.score-button')
      await buttons[1].trigger('keydown.enter')

      expect(wrapper.emitted('score-change')).toBeTruthy()
      expect(wrapper.emitted('score-change')![0]).toEqual([
        { competencyId: 'comp-1', score: 2 },
      ])
    })

    it('should handle Space key press', async () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: { competencyId: 'comp-1' },
      })

      const buttons = wrapper.findAll('.score-button')
      await buttons[2].trigger('keydown.space')

      expect(wrapper.emitted('score-change')).toBeTruthy()
      expect(wrapper.emitted('score-change')![0]).toEqual([
        { competencyId: 'comp-1', score: 3 },
      ])
    })

    it('should have aria-label describing the competency score card', () => {
      const wrapper = mount(CompetencyScoreCard, {
        props: { competencyId: 'comp-1' },
      })

      expect(wrapper.find('.competency-score-card').attributes('aria-label')).toBeDefined()
    })
  })
})
