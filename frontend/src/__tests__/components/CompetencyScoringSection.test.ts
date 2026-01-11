// TSS PPM v3.0 - CompetencyScoringSection Integration Tests
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { nextTick } from 'vue'
import CompetencyScoringSection from '../../components/review/CompetencyScoringSection.vue'
import type { Competency } from '../../types/competency'

// Mock the API
vi.mock('../../api/competencies', () => ({
  getCompetencies: vi.fn(),
}))

import { getCompetencies } from '../../api/competencies'

const mockGetCompetencies = vi.mocked(getCompetencies)

// Sample competencies
const mockCompetencies: Competency[] = [
  { id: 'comp-1', level: 'B', category: 'Dedicated', subcategory: 'Result driven', title_en: 'Result driven', display_order: 1 },
  { id: 'comp-2', level: 'B', category: 'Dedicated', subcategory: 'Committed', title_en: 'Committed', display_order: 2 },
  { id: 'comp-3', level: 'B', category: 'Entrepreneurial', subcategory: 'Entrepreneurial', title_en: 'Entrepreneurial', display_order: 3 },
  { id: 'comp-4', level: 'B', category: 'Entrepreneurial', subcategory: 'Ambition', title_en: 'Ambition', display_order: 4 },
  { id: 'comp-5', level: 'B', category: 'Innovative', subcategory: 'Market oriented', title_en: 'Market oriented', display_order: 5 },
  { id: 'comp-6', level: 'B', category: 'Innovative', subcategory: 'Customer focused', title_en: 'Customer focused', display_order: 6 },
]

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages: {
    en: {
      competencies: {
        title: 'Competencies',
        how: 'HOW (Competencies)',
        howScoreLabel: 'HOW Score',
        veto: 'VETO',
        vetoWarning: 'Score of 1 triggers VETO',
        scoreComplete: '{count}/6 competencies scored',
        categories: { Dedicated: 'Dedicated', Entrepreneurial: 'Entrepreneurial', Innovative: 'Innovative' },
        scores: { 1: 'Below', 2: 'Meets', 3: 'Exceeds' },
        notes: 'Notes',
        showIndicators: 'Show indicators',
        hideIndicators: 'Hide indicators',
      },
      scoring: {
        gridPosition: 'Grid Position',
        howScore: 'HOW Score',
        vetoActive: 'VETO Active',
        gridLabels: { how: { 1: 'Below', 2: 'Meets', 3: 'Exceeds' } },
      },
      common: { loading: 'Loading...' },
    },
  },
})

function createWrapper(props = {}) {
  return mount(CompetencyScoringSection, {
    props: {
      reviewId: 'review-123',
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

describe('CompetencyScoringSection', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    mockGetCompetencies.mockResolvedValue(mockCompetencies)
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('component rendering', () => {
    it('should display all components when loaded', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.competency-list').exists()).toBe(true)
      expect(wrapper.find('.how-score-indicator').exists()).toBe(true)
    })

    it('should display section title', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.section-title').text()).toContain('HOW')
    })
  })

  describe('end-to-end score entry', () => {
    it('should update HOW score when all scores are entered', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      // Click score buttons for all 6 competencies (all score 2)
      const scoreButtons = wrapper.findAll('.score-button')
      for (let i = 0; i < 6; i++) {
        await scoreButtons[i * 3 + 1].trigger('click') // Select score 2 (middle button)
      }

      await nextTick()

      const howScoreValue = wrapper.find('.how-score-value')
      expect(howScoreValue.text()).toBe('2.00')
    })
  })

  describe('auto-save triggers on score change', () => {
    it('should debounce save calls', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const scoreButtons = wrapper.findAll('.score-button')

      // Make multiple quick score changes
      await scoreButtons[0].trigger('click')
      await scoreButtons[3].trigger('click')
      await scoreButtons[6].trigger('click')

      // Advance timers less than debounce time
      await vi.advanceTimersByTimeAsync(500)
      expect(wrapper.emitted('score-save')).toBeFalsy()

      // Advance past debounce time
      await vi.advanceTimersByTimeAsync(600)
      expect(wrapper.emitted('score-save')).toBeTruthy()
      // Should only have one save call due to debouncing
      expect(wrapper.emitted('score-save')?.length).toBe(1)
    })

    it('should emit score-change event immediately', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const scoreButtons = wrapper.findAll('.score-button')
      await scoreButtons[0].trigger('click')

      expect(wrapper.emitted('score-change')).toBeTruthy()
    })
  })

  describe('9-Grid updates on HOW score change', () => {
    it('should emit how-score-change when score changes', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      // Enter all 6 scores
      const scoreButtons = wrapper.findAll('.score-button')
      for (let i = 0; i < 6; i++) {
        await scoreButtons[i * 3 + 2].trigger('click') // Select score 3
      }

      await nextTick()

      expect(wrapper.emitted('how-score-change')).toBeTruthy()
      const lastEvent = wrapper.emitted('how-score-change')!.pop()
      expect(lastEvent).toEqual([{ howScore: 3, gridPosition: 3, vetoActive: false }])
    })

    it('should emit VETO state when score 1 is selected', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      // Enter all 6 scores with one VETO (score 1)
      const scoreButtons = wrapper.findAll('.score-button')
      await scoreButtons[0].trigger('click') // First competency score 1 (VETO)
      for (let i = 1; i < 6; i++) {
        await scoreButtons[i * 3 + 1].trigger('click') // Rest score 2
      }

      await nextTick()

      expect(wrapper.emitted('how-score-change')).toBeTruthy()
      const lastEvent = wrapper.emitted('how-score-change')!.pop()
      expect(lastEvent).toEqual([{ howScore: 1, gridPosition: 1, vetoActive: true }])
    })
  })

  describe('progress tracking', () => {
    it('should show 0/6 initially', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('0/6')
    })

    it('should update progress as scores are entered', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const scoreButtons = wrapper.findAll('.score-button')
      await scoreButtons[0].trigger('click')
      await scoreButtons[3].trigger('click')
      await scoreButtons[6].trigger('click')

      await nextTick()

      expect(wrapper.text()).toContain('3/6')
    })
  })

  describe('VETO warning display', () => {
    it('should show VETO warning when score 1 is selected and complete', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      // Enter all 6 scores with one score = 1
      const scoreButtons = wrapper.findAll('.score-button')
      await scoreButtons[0].trigger('click') // Score 1

      for (let i = 1; i < 6; i++) {
        await scoreButtons[i * 3 + 1].trigger('click') // Score 2
      }

      await nextTick()

      expect(wrapper.find('.veto-banner').exists()).toBe(true)
    })
  })

  describe('initial scores loading', () => {
    it('should accept and display initial scores', async () => {
      const initialScores = {
        'comp-1': 2,
        'comp-2': 3,
        'comp-3': 2,
        'comp-4': 2,
        'comp-5': 3,
        'comp-6': 2,
      }

      const wrapper = createWrapper({ initialScores })
      await flushPromises()

      // Check that scores are reflected in the UI
      expect(wrapper.find('.how-score-value').text()).toBe('2.33')
    })
  })

  describe('disabled state', () => {
    it('should disable all interactions when disabled', async () => {
      const wrapper = createWrapper({ disabled: true })
      await flushPromises()

      const scoreCards = wrapper.findAll('.competency-score-card')
      scoreCards.forEach((card) => {
        expect(card.classes()).toContain('disabled')
      })
    })
  })
})
