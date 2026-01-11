// TSS PPM v3.0 - GoalScoringSection Component Tests
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import GoalScoringSection from '../../components/review/GoalScoringSection.vue'

// Mock VoiceInput component
vi.mock('../../components/common/VoiceInput.vue', () => ({
  default: {
    template: '<button class="voice-input-stub" @click="$emit(\'transcription\', \'test transcription\')">Voice</button>',
    emits: ['transcription'],
  },
}))

const mockGoals = [
  {
    id: 'goal-1',
    title: 'Increase Revenue',
    description: 'Achieve 10% revenue growth',
    weight: 40,
    goal_type: 'STANDARD',
  },
  {
    id: 'goal-2',
    title: 'Customer Satisfaction',
    description: 'Maintain NPS score above 50',
    weight: 30,
    goal_type: 'KAR',
  },
  {
    id: 'goal-3',
    title: 'Safety Compliance',
    description: 'Zero safety incidents',
    weight: 30,
    goal_type: 'SCF',
  },
]

describe('GoalScoringSection', () => {
  describe('goal list with score cards', () => {
    it('should render all goals', () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {} },
      })

      expect(wrapper.findAll('.goal-item')).toHaveLength(3)
    })

    it('should display goal title', () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {} },
      })

      expect(wrapper.text()).toContain('Increase Revenue')
      expect(wrapper.text()).toContain('Customer Satisfaction')
      expect(wrapper.text()).toContain('Safety Compliance')
    })

    it('should display goal weight', () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {} },
      })

      expect(wrapper.text()).toContain('40%')
      expect(wrapper.text()).toContain('30%')
    })

    it('should display goal type badge for KAR goals', () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {} },
      })

      const karBadge = wrapper.find('.goal-type-badge.kar')
      expect(karBadge.exists()).toBe(true)
      expect(karBadge.text()).toBe('KAR')
    })

    it('should display goal type badge for SCF goals', () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {} },
      })

      const scfBadge = wrapper.find('.goal-type-badge.scf')
      expect(scfBadge.exists()).toBe(true)
      expect(scfBadge.text()).toBe('SCF')
    })

    it('should render score card for each goal', () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {} },
      })

      const scoreCards = wrapper.findAllComponents({ name: 'ScoreCard' })
      expect(scoreCards).toHaveLength(3)
    })

    it('should pass selected score to score card', () => {
      const wrapper = mount(GoalScoringSection, {
        props: {
          goals: mockGoals,
          scores: {
            'goal-1': { score: 2, feedback: '' },
          },
        },
      })

      const firstGoalItem = wrapper.find('[data-goal-id="goal-1"]')
      const scoreCard = firstGoalItem.findComponent({ name: 'ScoreCard' })
      expect(scoreCard.props('modelValue')).toBe(2)
    })

    it('should emit score-change when score card is clicked', async () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {} },
      })

      const firstGoalItem = wrapper.find('[data-goal-id="goal-1"]')
      const scoreCard = firstGoalItem.findComponent({ name: 'ScoreCard' })
      await scoreCard.vm.$emit('update:modelValue', 3)

      expect(wrapper.emitted('score-change')).toBeTruthy()
      expect(wrapper.emitted('score-change')![0]).toEqual(['goal-1', 3])
    })
  })

  describe('feedback text area per goal', () => {
    it('should render feedback textarea for each goal', () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {} },
      })

      const textareas = wrapper.findAll('.goal-feedback textarea')
      expect(textareas).toHaveLength(3)
    })

    it('should display existing feedback', () => {
      const wrapper = mount(GoalScoringSection, {
        props: {
          goals: mockGoals,
          scores: {
            'goal-1': { score: 2, feedback: 'Good progress on revenue' },
          },
        },
      })

      const firstGoalItem = wrapper.find('[data-goal-id="goal-1"]')
      const textarea = firstGoalItem.find('.goal-feedback textarea')
      expect((textarea.element as HTMLTextAreaElement).value).toBe('Good progress on revenue')
    })

    it('should emit feedback-change when textarea changes', async () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {} },
      })

      const firstGoalItem = wrapper.find('[data-goal-id="goal-1"]')
      const textarea = firstGoalItem.find('.goal-feedback textarea')
      await textarea.setValue('New feedback')

      expect(wrapper.emitted('feedback-change')).toBeTruthy()
      expect(wrapper.emitted('feedback-change')![0]).toEqual(['goal-1', 'New feedback'])
    })

    it('should have placeholder text', () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {} },
      })

      const textarea = wrapper.find('.goal-feedback textarea')
      expect(textarea.attributes('placeholder')).toContain('feedback')
    })
  })

  describe('voice input integration', () => {
    it('should render voice input button for each goal', () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {} },
      })

      const voiceButtons = wrapper.findAll('.voice-input-stub')
      expect(voiceButtons).toHaveLength(3)
    })

    it('should append transcription to feedback when voice input completes', async () => {
      const wrapper = mount(GoalScoringSection, {
        props: {
          goals: mockGoals,
          scores: {
            'goal-1': { score: 2, feedback: 'Existing ' },
          },
        },
      })

      const firstGoalItem = wrapper.find('[data-goal-id="goal-1"]')
      const voiceButton = firstGoalItem.find('.voice-input-stub')
      await voiceButton.trigger('click')

      expect(wrapper.emitted('feedback-change')).toBeTruthy()
      expect(wrapper.emitted('feedback-change')![0]).toEqual(['goal-1', 'Existing test transcription'])
    })
  })

  describe('disabled state', () => {
    it('should disable score cards when disabled prop is true', () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {}, disabled: true },
      })

      const scoreCards = wrapper.findAllComponents({ name: 'ScoreCard' })
      scoreCards.forEach((card) => {
        expect(card.props('disabled')).toBe(true)
      })
    })

    it('should disable textareas when disabled prop is true', () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: mockGoals, scores: {}, disabled: true },
      })

      const textareas = wrapper.findAll('.goal-feedback textarea')
      textareas.forEach((textarea) => {
        expect(textarea.attributes('disabled')).toBeDefined()
      })
    })
  })

  describe('empty state', () => {
    it('should show empty message when no goals', () => {
      const wrapper = mount(GoalScoringSection, {
        props: { goals: [], scores: {} },
      })

      expect(wrapper.text()).toContain('No goals')
    })
  })
})
