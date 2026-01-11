// TSS PPM v3.0 - CompetencyPreview Component Tests
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import CompetencyPreview from '../../components/review/CompetencyPreview.vue'
import type { Competency } from '../../types/competency'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
    locale: { value: 'en' },
  }),
}))

const mockCompetencies: Competency[] = [
  {
    id: 'comp-1',
    level: 'B',
    category: 'Dedicated',
    subcategory: 'Result driven',
    title_en: 'Achieves Results',
    indicators_en: ['Delivers on commitments', 'Sets clear goals'],
    display_order: 1,
  },
  {
    id: 'comp-2',
    level: 'B',
    category: 'Dedicated',
    subcategory: 'Committed',
    title_en: 'Shows Commitment',
    indicators_en: ['Takes ownership', 'Perseveres through challenges'],
    display_order: 2,
  },
  {
    id: 'comp-3',
    level: 'B',
    category: 'Entrepreneurial',
    subcategory: 'Entrepreneurial',
    title_en: 'Takes Initiative',
    indicators_en: ['Identifies opportunities', 'Acts proactively'],
    display_order: 3,
  },
  {
    id: 'comp-4',
    level: 'B',
    category: 'Entrepreneurial',
    subcategory: 'Ambition',
    title_en: 'Drives Growth',
    indicators_en: ['Sets ambitious targets', 'Seeks improvement'],
    display_order: 4,
  },
  {
    id: 'comp-5',
    level: 'B',
    category: 'Innovative',
    subcategory: 'Market oriented',
    title_en: 'Understands Market',
    indicators_en: ['Monitors trends', 'Identifies customer needs'],
    display_order: 5,
  },
  {
    id: 'comp-6',
    level: 'B',
    category: 'Innovative',
    subcategory: 'Customer focused',
    title_en: 'Focuses on Customer',
    indicators_en: ['Builds relationships', 'Responds to feedback'],
    display_order: 6,
  },
]

describe('CompetencyPreview', () => {
  describe('displaying 6 competencies grouped by category', () => {
    it('should display all 6 competencies', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: mockCompetencies,
          loading: false,
        },
      })

      const competencyItems = wrapper.findAll('[data-testid="competency-item"]')
      expect(competencyItems.length).toBe(6)
    })

    it('should group competencies by category', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: mockCompetencies,
          loading: false,
        },
      })

      const categories = wrapper.findAll('.competency-category')
      expect(categories.length).toBe(3)
    })

    it('should display Dedicated category with 2 competencies', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: mockCompetencies,
          loading: false,
        },
      })

      const dedicatedCategory = wrapper.find('[data-testid="category-Dedicated"]')
      expect(dedicatedCategory.exists()).toBe(true)
      const items = dedicatedCategory.findAll('[data-testid="competency-item"]')
      expect(items.length).toBe(2)
    })

    it('should display Entrepreneurial category with 2 competencies', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: mockCompetencies,
          loading: false,
        },
      })

      const entrepreneurialCategory = wrapper.find('[data-testid="category-Entrepreneurial"]')
      expect(entrepreneurialCategory.exists()).toBe(true)
      const items = entrepreneurialCategory.findAll('[data-testid="competency-item"]')
      expect(items.length).toBe(2)
    })

    it('should display Innovative category with 2 competencies', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: mockCompetencies,
          loading: false,
        },
      })

      const innovativeCategory = wrapper.find('[data-testid="category-Innovative"]')
      expect(innovativeCategory.exists()).toBe(true)
      const items = innovativeCategory.findAll('[data-testid="competency-item"]')
      expect(items.length).toBe(2)
    })
  })

  describe('competency name and description display', () => {
    it('should display competency title', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: mockCompetencies,
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('Achieves Results')
      expect(wrapper.text()).toContain('Shows Commitment')
    })

    it('should display subcategory', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: mockCompetencies,
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('Result driven')
      expect(wrapper.text()).toContain('Committed')
    })
  })

  describe('empty state when no TOV level selected', () => {
    it('should display empty state when competencies array is empty', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: [],
          loading: false,
        },
      })

      expect(wrapper.find('[data-testid="empty-state"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('competencyPreview.emptyState')
    })

    it('should not display competency items when empty', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: [],
          loading: false,
        },
      })

      const competencyItems = wrapper.findAll('[data-testid="competency-item"]')
      expect(competencyItems.length).toBe(0)
    })

    it('should display select TOV level message in empty state', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: [],
          loading: false,
          showSelectMessage: true,
        },
      })

      expect(wrapper.text()).toContain('competencyPreview.selectTovLevel')
    })
  })

  describe('dynamic update on TOV level change', () => {
    it('should update displayed competencies when props change', async () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: mockCompetencies.slice(0, 2),
          loading: false,
        },
      })

      let items = wrapper.findAll('[data-testid="competency-item"]')
      expect(items.length).toBe(2)

      await wrapper.setProps({ competencies: mockCompetencies })

      items = wrapper.findAll('[data-testid="competency-item"]')
      expect(items.length).toBe(6)
    })

    it('should show loading state during fetch', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: [],
          loading: true,
        },
      })

      expect(wrapper.find('[data-testid="loading-state"]').exists()).toBe(true)
    })

    it('should hide loading state when fetch completes', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: mockCompetencies,
          loading: false,
        },
      })

      expect(wrapper.find('[data-testid="loading-state"]').exists()).toBe(false)
    })
  })

  describe('styling and layout', () => {
    it('should render with preview container class', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: mockCompetencies,
          loading: false,
        },
      })

      expect(wrapper.find('.competency-preview').exists()).toBe(true)
    })

    it('should display section header', () => {
      const wrapper = mount(CompetencyPreview, {
        props: {
          competencies: mockCompetencies,
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('competencyPreview.title')
    })
  })
})
