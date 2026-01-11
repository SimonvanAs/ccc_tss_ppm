// TSS PPM v3.0 - TeamDashboardView Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import TeamDashboardView from '../../views/TeamDashboardView.vue'
import { ScoringStatus } from '../../types'
import type { TeamMember } from '../../types'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'team.pageTitle': 'My Team',
        'team.pageSubtitle': 'Review and score your team members',
        'team.emptyState': 'No team members found',
        'team.loading': 'Loading team...',
        'team.error': 'Failed to load team',
        'scoring.notStarted': 'Not Started',
        'scoring.inProgress': 'In Progress',
        'scoring.complete': 'Complete',
      }
      return messages[key] || key
    },
  }),
}))

// Mock vue-router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

// Mock team API
vi.mock('../../api/team', () => ({
  fetchTeamMembers: vi.fn(),
}))

import * as teamApi from '../../api/team'

function createMockTeamMembers(): TeamMember[] {
  return [
    {
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
    },
    {
      id: 'user-2',
      email: 'jane@example.com',
      first_name: 'Jane',
      last_name: 'Smith',
      function_title: 'UX Designer',
      tov_level: 'C',
      review_id: 'review-2',
      review_stage: 'END_YEAR_REVIEW',
      review_status: 'DRAFT',
      scoring_status: ScoringStatus.IN_PROGRESS,
    },
    {
      id: 'user-3',
      email: 'bob@example.com',
      first_name: 'Bob',
      last_name: 'Wilson',
      function_title: 'Product Manager',
      tov_level: 'D',
      review_id: 'review-3',
      review_stage: 'END_YEAR_REVIEW',
      review_status: 'DRAFT',
      scoring_status: ScoringStatus.COMPLETE,
    },
  ]
}

describe('TeamDashboardView', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    mockPush.mockReset()
  })

  function createWrapper() {
    return mount(TeamDashboardView, {
      global: {
        stubs: {
          TeamMemberCard: {
            template: '<div class="team-member-card-stub" @click="$emit(\'click\')"><slot /></div>',
            props: ['member'],
          },
        },
      },
    })
  }

  describe('loading state', () => {
    it('should show loading state initially', async () => {
      vi.mocked(teamApi.fetchTeamMembers).mockImplementation(
        () => new Promise(() => {})  // Never resolves
      )

      const wrapper = createWrapper()

      expect(wrapper.text()).toContain('Loading')
    })
  })

  describe('team list rendering', () => {
    it('should fetch team members on mount', async () => {
      vi.mocked(teamApi.fetchTeamMembers).mockResolvedValue(createMockTeamMembers())

      createWrapper()
      await flushPromises()

      expect(teamApi.fetchTeamMembers).toHaveBeenCalled()
    })

    it('should render team members', async () => {
      vi.mocked(teamApi.fetchTeamMembers).mockResolvedValue(createMockTeamMembers())

      const wrapper = createWrapper()
      await flushPromises()

      const cards = wrapper.findAll('.team-member-card-stub')
      expect(cards).toHaveLength(3)
    })

    it('should show empty state when no team members', async () => {
      vi.mocked(teamApi.fetchTeamMembers).mockResolvedValue([])

      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('No team members found')
    })

    it('should show page title', async () => {
      vi.mocked(teamApi.fetchTeamMembers).mockResolvedValue(createMockTeamMembers())

      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('My Team')
    })
  })

  describe('error handling', () => {
    it('should show error message on API failure', async () => {
      vi.mocked(teamApi.fetchTeamMembers).mockRejectedValue(new Error('Network error'))

      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('Failed to load team')
    })
  })
})
