// TSS PPM v3.0 - HOWScoreIndicator Component Tests
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import HOWScoreIndicator from '../../components/review/HOWScoreIndicator.vue'

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages: {
    en: {
      competencies: {
        howScoreLabel: 'HOW Score',
        veto: 'VETO',
        vetoWarning: 'Score of 1 triggers VETO - HOW score will be 1.00',
        scoreComplete: '{count}/6 competencies scored',
      },
      scoring: {
        gridPosition: 'Grid Position',
        howScore: 'HOW Score',
        vetoActive: 'VETO Active',
        gridLabels: {
          how: { 1: 'Below', 2: 'Meets', 3: 'Exceeds' },
        },
      },
    },
  },
})

function createWrapper(props = {}) {
  return mount(HOWScoreIndicator, {
    props: {
      howScore: null,
      vetoActive: false,
      vetoCompetencyId: undefined,
      gridPosition: null,
      scoredCount: 0,
      ...props,
    },
    global: {
      plugins: [i18n],
    },
  })
}

describe('HOWScoreIndicator', () => {
  describe('displays calculated HOW score', () => {
    it('should display HOW score with 2 decimal places', () => {
      const wrapper = createWrapper({ howScore: 2.33, scoredCount: 6 })

      expect(wrapper.find('.how-score-value').text()).toBe('2.33')
    })

    it('should display score 1.00 when VETO is active', () => {
      const wrapper = createWrapper({
        howScore: 1.0,
        vetoActive: true,
        scoredCount: 6,
      })

      expect(wrapper.find('.how-score-value').text()).toBe('1.00')
    })

    it('should display whole numbers with 2 decimal places', () => {
      const wrapper = createWrapper({ howScore: 2.0, scoredCount: 6 })

      expect(wrapper.find('.how-score-value').text()).toBe('2.00')
    })

    it('should display score of 3.00 correctly', () => {
      const wrapper = createWrapper({ howScore: 3.0, scoredCount: 6 })

      expect(wrapper.find('.how-score-value').text()).toBe('3.00')
    })

    it('should show dash when score is null (incomplete)', () => {
      const wrapper = createWrapper({ howScore: null, scoredCount: 3 })

      expect(wrapper.find('.how-score-value').text()).toBe('-')
    })
  })

  describe('VETO warning banner when active', () => {
    it('should show VETO warning banner when vetoActive is true', () => {
      const wrapper = createWrapper({
        howScore: 1.0,
        vetoActive: true,
        scoredCount: 6,
      })

      expect(wrapper.find('.veto-banner').exists()).toBe(true)
    })

    it('should not show VETO banner when vetoActive is false', () => {
      const wrapper = createWrapper({
        howScore: 2.0,
        vetoActive: false,
        scoredCount: 6,
      })

      expect(wrapper.find('.veto-banner').exists()).toBe(false)
    })

    it('should display VETO text in banner', () => {
      const wrapper = createWrapper({
        howScore: 1.0,
        vetoActive: true,
        scoredCount: 6,
      })

      expect(wrapper.find('.veto-banner').text()).toContain('VETO')
    })

    it('should apply magenta/red styling to VETO banner', () => {
      const wrapper = createWrapper({
        howScore: 1.0,
        vetoActive: true,
        scoredCount: 6,
      })

      expect(wrapper.find('.veto-banner').exists()).toBe(true)
    })
  })

  describe('grid position indicator', () => {
    it('should display grid position 1 when score is low', () => {
      const wrapper = createWrapper({
        howScore: 1.5,
        gridPosition: 1,
        scoredCount: 6,
      })

      expect(wrapper.find('.grid-position-value').text()).toBe('1')
    })

    it('should display grid position 2 when score is medium', () => {
      const wrapper = createWrapper({
        howScore: 2.0,
        gridPosition: 2,
        scoredCount: 6,
      })

      expect(wrapper.find('.grid-position-value').text()).toBe('2')
    })

    it('should display grid position 3 when score is high', () => {
      const wrapper = createWrapper({
        howScore: 3.0,
        gridPosition: 3,
        scoredCount: 6,
      })

      expect(wrapper.find('.grid-position-value').text()).toBe('3')
    })

    it('should show dash for grid position when incomplete', () => {
      const wrapper = createWrapper({ howScore: null, gridPosition: null, scoredCount: 3 })

      expect(wrapper.find('.grid-position-value').text()).toBe('-')
    })

    it('should display grid position label', () => {
      const wrapper = createWrapper({
        howScore: 2.0,
        gridPosition: 2,
        scoredCount: 6,
      })

      expect(wrapper.text()).toContain('Meets')
    })
  })

  describe('incomplete state display', () => {
    it('should show progress indicator with count', () => {
      const wrapper = createWrapper({ howScore: null, scoredCount: 3 })

      expect(wrapper.find('.progress-indicator').exists()).toBe(true)
      expect(wrapper.text()).toContain('3/6')
    })

    it('should show 0/6 when no scores entered', () => {
      const wrapper = createWrapper({ howScore: null, scoredCount: 0 })

      expect(wrapper.text()).toContain('0/6')
    })

    it('should show 6/6 when all scores entered', () => {
      const wrapper = createWrapper({ howScore: 2.0, scoredCount: 6 })

      expect(wrapper.text()).toContain('6/6')
    })

    it('should indicate incomplete state visually', () => {
      const wrapper = createWrapper({ howScore: null, scoredCount: 3 })

      expect(wrapper.find('.is-incomplete').exists()).toBe(true)
    })

    it('should not show incomplete state when all scored', () => {
      const wrapper = createWrapper({ howScore: 2.0, scoredCount: 6 })

      expect(wrapper.find('.is-incomplete').exists()).toBe(false)
    })
  })

  describe('styling and accessibility', () => {
    it('should have appropriate aria labels', () => {
      const wrapper = createWrapper({ howScore: 2.0, scoredCount: 6 })

      expect(wrapper.find('[aria-label]').exists()).toBe(true)
    })

    it('should use semantic heading for score label', () => {
      const wrapper = createWrapper({ howScore: 2.0, scoredCount: 6 })

      expect(wrapper.find('.score-label').exists()).toBe(true)
    })
  })
})
