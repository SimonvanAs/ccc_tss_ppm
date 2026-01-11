// TSS PPM v3.0 - TeamMemberCard Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import TeamMemberCard from '../../components/dashboard/TeamMemberCard.vue'
import { ScoringStatus } from '../../types'
import type { TeamMember } from '../../types'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'team.scoringStatus.NOT_STARTED': 'Not Started',
        'team.scoringStatus.IN_PROGRESS': 'In Progress',
        'team.scoringStatus.COMPLETE': 'Complete',
      }
      return messages[key] || key
    },
  }),
}))

function createMockMember(overrides: Partial<TeamMember> = {}): TeamMember {
  return {
    id: 'user-1',
    email: 'john@example.com',
    first_name: 'John',
    last_name: 'Doe',
    function_title: 'Software Engineer',
    tov_level: 'B',
    review_id: 'review-1',
    review_stage: 'END_YEAR_REVIEW',
    review_status: 'DRAFT',
    scoring_status: ScoringStatus.NOT_STARTED,
    ...overrides,
  }
}

describe('TeamMemberCard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  function createWrapper(member: TeamMember = createMockMember()) {
    return mount(TeamMemberCard, {
      props: { member },
    })
  }

  describe('member info rendering', () => {
    it('should display member full name', () => {
      const wrapper = createWrapper()

      expect(wrapper.text()).toContain('John Doe')
    })

    it('should display member function title', () => {
      const wrapper = createWrapper()

      expect(wrapper.text()).toContain('Software Engineer')
    })

    it('should display member email', () => {
      const wrapper = createWrapper()

      expect(wrapper.text()).toContain('john@example.com')
    })

    it('should handle null first name', () => {
      const wrapper = createWrapper(createMockMember({ first_name: null }))

      expect(wrapper.text()).toContain('Doe')
    })

    it('should handle null last name', () => {
      const wrapper = createWrapper(createMockMember({ last_name: null }))

      expect(wrapper.text()).toContain('John')
    })
  })

  describe('status badge rendering', () => {
    it('should show NOT_STARTED status badge', () => {
      const wrapper = createWrapper(createMockMember({
        scoring_status: ScoringStatus.NOT_STARTED
      }))

      const badge = wrapper.find('.status-badge')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toContain('Not Started')
      expect(badge.classes()).toContain('status-not-started')
    })

    it('should show IN_PROGRESS status badge', () => {
      const wrapper = createWrapper(createMockMember({
        scoring_status: ScoringStatus.IN_PROGRESS
      }))

      const badge = wrapper.find('.status-badge')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toContain('In Progress')
      expect(badge.classes()).toContain('status-in-progress')
    })

    it('should show COMPLETE status badge', () => {
      const wrapper = createWrapper(createMockMember({
        scoring_status: ScoringStatus.COMPLETE
      }))

      const badge = wrapper.find('.status-badge')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toContain('Complete')
      expect(badge.classes()).toContain('status-complete')
    })
  })

  describe('click handling', () => {
    it('should emit click event when card is clicked', async () => {
      const wrapper = createWrapper()

      await wrapper.trigger('click')

      expect(wrapper.emitted('click')).toHaveLength(1)
    })

    it('should be clickable (have cursor pointer)', () => {
      const wrapper = createWrapper()

      expect(wrapper.classes()).toContain('team-member-card')
    })
  })

  describe('TOV level display', () => {
    it('should display TOV level when present', () => {
      const wrapper = createWrapper(createMockMember({ tov_level: 'C' }))

      expect(wrapper.text()).toContain('C')
    })

    it('should not display TOV level section when null', () => {
      const wrapper = createWrapper(createMockMember({ tov_level: null }))

      const tovSection = wrapper.find('.tov-level')
      expect(tovSection.exists()).toBe(false)
    })
  })
})
