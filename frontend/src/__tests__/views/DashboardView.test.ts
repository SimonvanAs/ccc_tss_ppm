// TSS PPM v3.0 - DashboardView Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DashboardView from '../../views/DashboardView.vue'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'dashboard.title': 'Dashboard',
        'dashboard.welcome': 'Welcome to TSS PPM',
      }
      return messages[key] || key
    },
  }),
}))

// Mock vue-router
vi.mock('vue-router', () => ({
  RouterLink: {
    template: '<a :href="to" class="router-link"><slot /></a>',
    props: ['to'],
  },
}))

// Mock auth API
vi.mock('../../api/auth', () => ({
  getCurrentUser: vi.fn(),
  logout: vi.fn(),
}))

import * as auth from '../../api/auth'

describe('DashboardView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  function createWrapper() {
    return mount(DashboardView, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a :href="to" class="router-link"><slot /></a>',
            props: ['to'],
          },
          Card: {
            template: '<div class="card-stub"><slot /></div>',
          },
          SectionHeader: {
            template: '<div class="section-header-stub"><slot name="subtitle" /></div>',
            props: ['title'],
          },
        },
      },
    })
  }

  describe('page rendering', () => {
    it('should render the dashboard page', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue(null)

      const wrapper = createWrapper()

      expect(wrapper.find('.dashboard').exists()).toBe(true)
    })

    it('should render quick links section', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue(null)

      const wrapper = createWrapper()

      expect(wrapper.text()).toContain('Quick Links')
      expect(wrapper.text()).toContain('Go to Goal Setting (Demo)')
    })
  })

  describe('user info display', () => {
    it('should display user info when user is logged in', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue({
        email: 'user@example.com',
        name: 'Test User',
        roles: ['employee', 'manager'],
      })

      const wrapper = createWrapper()

      expect(wrapper.text()).toContain('user@example.com')
      expect(wrapper.text()).toContain('Test User')
      expect(wrapper.text()).toContain('employee, manager')
    })

    it('should not display user info when user is not logged in', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue(null)

      const wrapper = createWrapper()

      expect(wrapper.text()).not.toContain('Logged in as')
    })

    it('should call logout when logout button is clicked', async () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue({
        email: 'user@example.com',
        name: 'Test User',
        roles: ['employee'],
      })

      const wrapper = createWrapper()
      await wrapper.find('.logout-btn').trigger('click')

      expect(auth.logout).toHaveBeenCalled()
    })
  })

  describe('layout components', () => {
    it('should use Card and SectionHeader components', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue({
        email: 'user@example.com',
        name: 'Test User',
        roles: ['employee'],
      })

      const wrapper = createWrapper()

      expect(wrapper.find('.section-header-stub').exists()).toBe(true)
      expect(wrapper.findAll('.card-stub').length).toBeGreaterThan(0)
    })
  })
})
