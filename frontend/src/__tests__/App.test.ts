// TSS PPM v3.0 - App Navigation Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import App from '../App.vue'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'app.title': 'TSS PPM',
        'nav.dashboard': 'Dashboard',
        'nav.team': 'Team',
      }
      return messages[key] || key
    },
    locale: { value: 'en' },
  }),
}))

// Mock auth API
vi.mock('../api/auth', () => ({
  getCurrentUser: vi.fn(),
}))

import * as auth from '../api/auth'

describe('App Navigation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  function createWrapper() {
    return mount(App, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a :href="to" class="router-link" :class="$attrs.class"><slot /></a>',
            props: ['to'],
          },
          RouterView: {
            template: '<div class="router-view-stub"></div>',
          },
        },
      },
    })
  }

  describe('role-based navigation', () => {
    it('should show Dashboard link for all users', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue({
        email: 'user@example.com',
        name: 'Test User',
        roles: ['employee'],
      })

      const wrapper = createWrapper()

      expect(wrapper.text()).toContain('Dashboard')
    })

    it('should show Team link for managers', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue({
        email: 'manager@example.com',
        name: 'Test Manager',
        roles: ['manager', 'employee'],
      })

      const wrapper = createWrapper()

      expect(wrapper.text()).toContain('Team')
    })

    it('should NOT show Team link for employees without manager role', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue({
        email: 'employee@example.com',
        name: 'Test Employee',
        roles: ['employee'],
      })

      const wrapper = createWrapper()

      expect(wrapper.text()).not.toContain('Team')
    })

    it('should handle null user gracefully', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue(null)

      const wrapper = createWrapper()

      // Should still render without crashing
      expect(wrapper.text()).toContain('Dashboard')
      expect(wrapper.text()).not.toContain('Team')
    })

    it('should handle user without roles array', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue({
        email: 'user@example.com',
        name: 'Test User',
        roles: undefined as unknown as string[],
      })

      const wrapper = createWrapper()

      expect(wrapper.text()).not.toContain('Team')
    })
  })

  describe('language switcher', () => {
    it('should render language buttons', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue(null)

      const wrapper = createWrapper()

      expect(wrapper.text()).toContain('EN')
      expect(wrapper.text()).toContain('NL')
      expect(wrapper.text()).toContain('ES')
    })
  })
})
