// TSS PPM v3.0 - CompetencyScoringSection Component Tests
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CompetencyScoringSection from '../../components/review/CompetencyScoringSection.vue'

const mockCompetencies = [
  {
    id: 'comp-1',
    name: 'Result Driven',
    description: 'Focus on achieving goals',
    category: 'Dedicated',
  },
  {
    id: 'comp-2',
    name: 'Committed',
    description: 'Dedication to work',
    category: 'Dedicated',
  },
  {
    id: 'comp-3',
    name: 'Entrepreneurial',
    description: 'Takes initiative',
    category: 'Entrepreneurial',
  },
  {
    id: 'comp-4',
    name: 'Ambition',
    description: 'Strives for excellence',
    category: 'Entrepreneurial',
  },
  {
    id: 'comp-5',
    name: 'Market Oriented',
    description: 'Understands market dynamics',
    category: 'Innovative',
  },
  {
    id: 'comp-6',
    name: 'Customer Focused',
    description: 'Prioritizes customer needs',
    category: 'Innovative',
  },
]

describe('CompetencyScoringSection', () => {
  describe('competency list by category', () => {
    it('should group competencies by category', () => {
      const wrapper = mount(CompetencyScoringSection, {
        props: { competencies: mockCompetencies, scores: {} },
      })

      const categories = wrapper.findAll('.category-group')
      expect(categories).toHaveLength(3)
    })

    it('should display category headers', () => {
      const wrapper = mount(CompetencyScoringSection, {
        props: { competencies: mockCompetencies, scores: {} },
      })

      expect(wrapper.text()).toContain('Dedicated')
      expect(wrapper.text()).toContain('Entrepreneurial')
      expect(wrapper.text()).toContain('Innovative')
    })

    it('should display all competencies', () => {
      const wrapper = mount(CompetencyScoringSection, {
        props: { competencies: mockCompetencies, scores: {} },
      })

      const items = wrapper.findAll('.competency-item')
      expect(items).toHaveLength(6)
    })

    it('should display competency name', () => {
      const wrapper = mount(CompetencyScoringSection, {
        props: { competencies: mockCompetencies, scores: {} },
      })

      expect(wrapper.text()).toContain('Result Driven')
      expect(wrapper.text()).toContain('Customer Focused')
    })

    it('should display competency description', () => {
      const wrapper = mount(CompetencyScoringSection, {
        props: { competencies: mockCompetencies, scores: {} },
      })

      expect(wrapper.text()).toContain('Focus on achieving goals')
    })
  })

  describe('score cards per competency', () => {
    it('should render score card for each competency', () => {
      const wrapper = mount(CompetencyScoringSection, {
        props: { competencies: mockCompetencies, scores: {} },
      })

      const scoreCards = wrapper.findAllComponents({ name: 'ScoreCard' })
      expect(scoreCards).toHaveLength(6)
    })

    it('should pass selected score to score card', () => {
      const wrapper = mount(CompetencyScoringSection, {
        props: {
          competencies: mockCompetencies,
          scores: {
            'comp-1': { score: 3 },
          },
        },
      })

      const firstItem = wrapper.find('[data-competency-id="comp-1"]')
      const scoreCard = firstItem.findComponent({ name: 'ScoreCard' })
      expect(scoreCard.props('modelValue')).toBe(3)
    })

    it('should emit score-change when score card is clicked', async () => {
      const wrapper = mount(CompetencyScoringSection, {
        props: { competencies: mockCompetencies, scores: {} },
      })

      const firstItem = wrapper.find('[data-competency-id="comp-1"]')
      const scoreCard = firstItem.findComponent({ name: 'ScoreCard' })
      await scoreCard.vm.$emit('update:modelValue', 2)

      expect(wrapper.emitted('score-change')).toBeTruthy()
      expect(wrapper.emitted('score-change')![0]).toEqual(['comp-1', 2])
    })

    it('should disable score cards when disabled prop is true', () => {
      const wrapper = mount(CompetencyScoringSection, {
        props: { competencies: mockCompetencies, scores: {}, disabled: true },
      })

      const scoreCards = wrapper.findAllComponents({ name: 'ScoreCard' })
      scoreCards.forEach((card) => {
        expect(card.props('disabled')).toBe(true)
      })
    })
  })

  describe('section header', () => {
    it('should display section title', () => {
      const wrapper = mount(CompetencyScoringSection, {
        props: { competencies: mockCompetencies, scores: {} },
      })

      expect(wrapper.find('.section-title').text()).toContain('Competencies')
      expect(wrapper.find('.section-title').text()).toContain('HOW')
    })
  })

  describe('empty state', () => {
    it('should show empty message when no competencies', () => {
      const wrapper = mount(CompetencyScoringSection, {
        props: { competencies: [], scores: {} },
      })

      expect(wrapper.text()).toContain('No competencies')
    })
  })

  describe('compact mode', () => {
    it('should apply compact class when compact prop is true', () => {
      const wrapper = mount(CompetencyScoringSection, {
        props: { competencies: mockCompetencies, scores: {}, compact: true },
      })

      expect(wrapper.find('.competency-scoring-section').classes()).toContain('compact')
    })
  })
})
