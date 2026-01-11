// TSS PPM v3.0 - ScoreCard Component Tests
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ScoreCard from '../../components/review/ScoreCard.vue'

describe('ScoreCard', () => {
  describe('three-card display', () => {
    it('should render three score options (1, 2, 3)', () => {
      const wrapper = mount(ScoreCard)

      const cards = wrapper.findAll('.score-option')
      expect(cards).toHaveLength(3)

      expect(cards[0].text()).toContain('1')
      expect(cards[1].text()).toContain('2')
      expect(cards[2].text()).toContain('3')
    })

    it('should render labels for each score', () => {
      const wrapper = mount(ScoreCard, {
        props: {
          labels: {
            1: 'Does not meet',
            2: 'Meets expectations',
            3: 'Exceeds expectations',
          },
        },
      })

      const cards = wrapper.findAll('.score-option')
      expect(cards[0].text()).toContain('Does not meet')
      expect(cards[1].text()).toContain('Meets expectations')
      expect(cards[2].text()).toContain('Exceeds expectations')
    })

    it('should display score number prominently', () => {
      const wrapper = mount(ScoreCard)

      const scoreNumbers = wrapper.findAll('.score-number')
      expect(scoreNumbers).toHaveLength(3)
      expect(scoreNumbers[0].text()).toBe('1')
      expect(scoreNumbers[1].text()).toBe('2')
      expect(scoreNumbers[2].text()).toBe('3')
    })
  })

  describe('selection state', () => {
    it('should show no selection when modelValue is null', () => {
      const wrapper = mount(ScoreCard, {
        props: { modelValue: null },
      })

      const selectedCards = wrapper.findAll('.score-option.selected')
      expect(selectedCards).toHaveLength(0)
    })

    it('should highlight selected score of 1', () => {
      const wrapper = mount(ScoreCard, {
        props: { modelValue: 1 },
      })

      const cards = wrapper.findAll('.score-option')
      expect(cards[0].classes()).toContain('selected')
      expect(cards[1].classes()).not.toContain('selected')
      expect(cards[2].classes()).not.toContain('selected')
    })

    it('should highlight selected score of 2', () => {
      const wrapper = mount(ScoreCard, {
        props: { modelValue: 2 },
      })

      const cards = wrapper.findAll('.score-option')
      expect(cards[0].classes()).not.toContain('selected')
      expect(cards[1].classes()).toContain('selected')
      expect(cards[2].classes()).not.toContain('selected')
    })

    it('should highlight selected score of 3', () => {
      const wrapper = mount(ScoreCard, {
        props: { modelValue: 3 },
      })

      const cards = wrapper.findAll('.score-option')
      expect(cards[0].classes()).not.toContain('selected')
      expect(cards[1].classes()).not.toContain('selected')
      expect(cards[2].classes()).toContain('selected')
    })

    it('should apply score-1 class for danger styling', () => {
      const wrapper = mount(ScoreCard, {
        props: { modelValue: 1 },
      })

      const cards = wrapper.findAll('.score-option')
      expect(cards[0].classes()).toContain('score-1')
    })

    it('should apply score-2 class for warning styling', () => {
      const wrapper = mount(ScoreCard, {
        props: { modelValue: 2 },
      })

      const cards = wrapper.findAll('.score-option')
      expect(cards[1].classes()).toContain('score-2')
    })

    it('should apply score-3 class for success styling', () => {
      const wrapper = mount(ScoreCard, {
        props: { modelValue: 3 },
      })

      const cards = wrapper.findAll('.score-option')
      expect(cards[2].classes()).toContain('score-3')
    })
  })

  describe('click handler', () => {
    it('should emit update:modelValue when clicking score 1', async () => {
      const wrapper = mount(ScoreCard)

      const cards = wrapper.findAll('.score-option')
      await cards[0].trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([1])
    })

    it('should emit update:modelValue when clicking score 2', async () => {
      const wrapper = mount(ScoreCard)

      const cards = wrapper.findAll('.score-option')
      await cards[1].trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([2])
    })

    it('should emit update:modelValue when clicking score 3', async () => {
      const wrapper = mount(ScoreCard)

      const cards = wrapper.findAll('.score-option')
      await cards[2].trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([3])
    })

    it('should emit change event with new score', async () => {
      const wrapper = mount(ScoreCard)

      const cards = wrapper.findAll('.score-option')
      await cards[1].trigger('click')

      expect(wrapper.emitted('change')).toBeTruthy()
      expect(wrapper.emitted('change')![0]).toEqual([2])
    })

    it('should allow re-selecting the same score', async () => {
      const wrapper = mount(ScoreCard, {
        props: { modelValue: 2 },
      })

      const cards = wrapper.findAll('.score-option')
      await cards[1].trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([2])
    })
  })

  describe('disabled state', () => {
    it('should apply disabled class when disabled prop is true', () => {
      const wrapper = mount(ScoreCard, {
        props: { disabled: true },
      })

      expect(wrapper.find('.score-card').classes()).toContain('disabled')
    })

    it('should not emit events when disabled', async () => {
      const wrapper = mount(ScoreCard, {
        props: { disabled: true },
      })

      const cards = wrapper.findAll('.score-option')
      await cards[0].trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeFalsy()
      expect(wrapper.emitted('change')).toBeFalsy()
    })

    it('should show selection even when disabled', () => {
      const wrapper = mount(ScoreCard, {
        props: { modelValue: 2, disabled: true },
      })

      const cards = wrapper.findAll('.score-option')
      expect(cards[1].classes()).toContain('selected')
    })
  })

  describe('accessibility', () => {
    it('should have role="radiogroup"', () => {
      const wrapper = mount(ScoreCard)

      expect(wrapper.find('.score-card').attributes('role')).toBe('radiogroup')
    })

    it('should have role="radio" for each option', () => {
      const wrapper = mount(ScoreCard)

      const cards = wrapper.findAll('.score-option')
      cards.forEach((card) => {
        expect(card.attributes('role')).toBe('radio')
      })
    })

    it('should have aria-checked for selected option', () => {
      const wrapper = mount(ScoreCard, {
        props: { modelValue: 2 },
      })

      const cards = wrapper.findAll('.score-option')
      expect(cards[0].attributes('aria-checked')).toBe('false')
      expect(cards[1].attributes('aria-checked')).toBe('true')
      expect(cards[2].attributes('aria-checked')).toBe('false')
    })

    it('should be keyboard accessible with tabindex', () => {
      const wrapper = mount(ScoreCard)

      const cards = wrapper.findAll('.score-option')
      cards.forEach((card) => {
        expect(card.attributes('tabindex')).toBe('0')
      })
    })

    it('should handle Enter key press', async () => {
      const wrapper = mount(ScoreCard)

      const cards = wrapper.findAll('.score-option')
      await cards[1].trigger('keydown.enter')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([2])
    })

    it('should handle Space key press', async () => {
      const wrapper = mount(ScoreCard)

      const cards = wrapper.findAll('.score-option')
      await cards[2].trigger('keydown.space')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0]).toEqual([3])
    })
  })
})
