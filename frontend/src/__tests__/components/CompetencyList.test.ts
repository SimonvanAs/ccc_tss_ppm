// TSS PPM v3.0 - CompetencyList Component Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import CompetencyList from '../../components/review/CompetencyList.vue'
import type { Competency } from '../../types/competency'

// Mock the API
vi.mock('../../api/competencies', () => ({
  getCompetencies: vi.fn(),
}))

import { getCompetencies } from '../../api/competencies'

const mockGetCompetencies = vi.mocked(getCompetencies)

// Sample competencies for testing (6 competencies as per business requirement)
const mockCompetencies: Competency[] = [
  {
    id: 'comp-1',
    level: 'B',
    category: 'Dedicated',
    subcategory: 'Result driven',
    title_en: 'Result driven competency',
    indicators_en: ['Indicator 1', 'Indicator 2'],
    display_order: 1,
  },
  {
    id: 'comp-2',
    level: 'B',
    category: 'Dedicated',
    subcategory: 'Committed',
    title_en: 'Committed competency',
    indicators_en: ['Indicator 3'],
    display_order: 2,
  },
  {
    id: 'comp-3',
    level: 'B',
    category: 'Entrepreneurial',
    subcategory: 'Entrepreneurial',
    title_en: 'Entrepreneurial competency',
    indicators_en: ['Indicator 4'],
    display_order: 3,
  },
  {
    id: 'comp-4',
    level: 'B',
    category: 'Entrepreneurial',
    subcategory: 'Ambition',
    title_en: 'Ambition competency',
    indicators_en: ['Indicator 5'],
    display_order: 4,
  },
  {
    id: 'comp-5',
    level: 'B',
    category: 'Innovative',
    subcategory: 'Market oriented',
    title_en: 'Market oriented competency',
    indicators_en: ['Indicator 6'],
    display_order: 5,
  },
  {
    id: 'comp-6',
    level: 'B',
    category: 'Innovative',
    subcategory: 'Customer focused',
    title_en: 'Customer focused competency',
    indicators_en: ['Indicator 7'],
    display_order: 6,
  },
]

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages: {
    en: {
      competencies: {
        title: 'Competencies',
        how: 'HOW (Competencies)',
        categories: {
          Dedicated: 'Dedicated',
          Entrepreneurial: 'Entrepreneurial',
          Innovative: 'Innovative',
        },
        showIndicators: 'Show indicators',
        hideIndicators: 'Hide indicators',
        notes: 'Notes',
        scores: { 1: 'Below', 2: 'Meets', 3: 'Exceeds' },
        veto: 'VETO',
        vetoWarning: 'Score of 1 triggers VETO',
      },
      common: {
        loading: 'Loading...',
      },
    },
  },
})

function createWrapper(props = {}) {
  return mount(CompetencyList, {
    props: {
      tovLevel: 'B',
      ...props,
    },
    global: {
      plugins: [i18n],
      stubs: {
        VoiceInput: true,
      },
    },
  })
}

describe('CompetencyList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetCompetencies.mockResolvedValue(mockCompetencies)
  })

  describe('fetches competencies for TOV level', () => {
    it('should fetch competencies on mount', async () => {
      createWrapper({ tovLevel: 'B' })
      await flushPromises()

      expect(mockGetCompetencies).toHaveBeenCalledWith('B')
    })

    it('should show loading state while fetching', () => {
      // Don't resolve immediately
      mockGetCompetencies.mockReturnValue(new Promise(() => {}))
      const wrapper = createWrapper()

      expect(wrapper.find('.loading-state').exists()).toBe(true)
    })

    it('should hide loading state after fetch completes', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.loading-state').exists()).toBe(false)
    })

    it('should refetch when tovLevel prop changes', async () => {
      const wrapper = createWrapper({ tovLevel: 'A' })
      await flushPromises()

      expect(mockGetCompetencies).toHaveBeenCalledWith('A')

      await wrapper.setProps({ tovLevel: 'C' })
      await flushPromises()

      expect(mockGetCompetencies).toHaveBeenCalledWith('C')
    })
  })

  describe('renders 6 competencies grouped by category', () => {
    it('should render all 6 competencies', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const competencyItems = wrapper.findAll('.competency-item')
      expect(competencyItems).toHaveLength(6)
    })

    it('should group competencies by category', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const categoryGroups = wrapper.findAll('.category-group')
      expect(categoryGroups).toHaveLength(3)
    })

    it('should display Dedicated category with 2 competencies', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const dedicatedGroup = wrapper.find('[data-category="Dedicated"]')
      expect(dedicatedGroup.exists()).toBe(true)

      const items = dedicatedGroup.findAll('.competency-item')
      expect(items).toHaveLength(2)
    })

    it('should display Entrepreneurial category with 2 competencies', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const group = wrapper.find('[data-category="Entrepreneurial"]')
      expect(group.exists()).toBe(true)

      const items = group.findAll('.competency-item')
      expect(items).toHaveLength(2)
    })

    it('should display Innovative category with 2 competencies', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const group = wrapper.find('[data-category="Innovative"]')
      expect(group.exists()).toBe(true)

      const items = group.findAll('.competency-item')
      expect(items).toHaveLength(2)
    })

    it('should display competency title', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('Result driven competency')
    })

    it('should display category badge', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const badges = wrapper.findAll('.category-badge')
      expect(badges.length).toBeGreaterThan(0)
    })
  })

  describe('score card integration', () => {
    it('should render CompetencyScoreCard for each competency', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const scoreCards = wrapper.findAll('.competency-score-card')
      expect(scoreCards).toHaveLength(6)
    })

    it('should emit score-change when score card is clicked', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const scoreButton = wrapper.find('.score-button')
      await scoreButton.trigger('click')

      expect(wrapper.emitted('score-change')).toBeTruthy()
    })

    it('should pass current score to score card', async () => {
      const wrapper = createWrapper({
        tovLevel: 'B',
        scores: { 'comp-1': 2 },
      })
      await flushPromises()

      const firstItem = wrapper.find('[data-competency-id="comp-1"]')
      const selectedButton = firstItem.find('.score-button.selected')
      expect(selectedButton.exists()).toBe(true)
    })
  })

  describe('notes textarea with voice input', () => {
    it('should render notes textarea for each competency', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const textareas = wrapper.findAll('.notes-textarea')
      expect(textareas).toHaveLength(6)
    })

    it('should render VoiceInput component for each competency', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const voiceInputs = wrapper.findAll('voice-input-stub')
      expect(voiceInputs).toHaveLength(6)
    })

    it('should emit notes-change when notes are updated', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const textarea = wrapper.find('.notes-textarea')
      await textarea.setValue('Test note')
      await textarea.trigger('blur')

      expect(wrapper.emitted('notes-change')).toBeTruthy()
      expect(wrapper.emitted('notes-change')![0]).toEqual([
        { competencyId: 'comp-1', notes: 'Test note' },
      ])
    })
  })

  describe('VETO highlight on score = 1', () => {
    it('should highlight competency row when score is 1', async () => {
      const wrapper = createWrapper({
        tovLevel: 'B',
        scores: { 'comp-1': 1 },
      })
      await flushPromises()

      const firstItem = wrapper.find('[data-competency-id="comp-1"]')
      expect(firstItem.classes()).toContain('veto-warning')
    })

    it('should not highlight when score is 2 or 3', async () => {
      const wrapper = createWrapper({
        tovLevel: 'B',
        scores: { 'comp-1': 2 },
      })
      await flushPromises()

      const firstItem = wrapper.find('[data-competency-id="comp-1"]')
      expect(firstItem.classes()).not.toContain('veto-warning')
    })

    it('should show VETO indicator when score is 1', async () => {
      const wrapper = createWrapper({
        tovLevel: 'B',
        scores: { 'comp-1': 1 },
      })
      await flushPromises()

      const firstItem = wrapper.find('[data-competency-id="comp-1"]')
      expect(firstItem.find('.veto-indicator').exists()).toBe(true)
    })
  })

  describe('behavioral indicators', () => {
    it('should have toggle button for indicators', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const toggleButtons = wrapper.findAll('.indicators-toggle')
      expect(toggleButtons.length).toBeGreaterThan(0)
    })

    it('should show indicators when toggle is clicked', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const toggle = wrapper.find('.indicators-toggle')
      await toggle.trigger('click')

      expect(wrapper.find('.indicators-list').exists()).toBe(true)
    })
  })

  describe('disabled state', () => {
    it('should disable all score cards when disabled prop is true', async () => {
      const wrapper = createWrapper({ disabled: true })
      await flushPromises()

      const scoreCards = wrapper.findAll('.competency-score-card')
      scoreCards.forEach((card) => {
        expect(card.classes()).toContain('disabled')
      })
    })

    it('should disable notes textareas when disabled', async () => {
      const wrapper = createWrapper({ disabled: true })
      await flushPromises()

      const textareas = wrapper.findAll('.notes-textarea')
      textareas.forEach((textarea) => {
        expect(textarea.attributes('disabled')).toBeDefined()
      })
    })
  })
})
