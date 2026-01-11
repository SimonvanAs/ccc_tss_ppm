// TSS PPM v3.0 - App Navigation Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import App from '../App.vue'

// Mock vue-router
const mockRoute = ref({ path: '/' })
vi.mock('vue-router', () => ({
  useRoute: () => mockRoute.value,
  RouterLink: {
    template: '<a :href="to" class="router-link"><slot /></a>',
    props: ['to'],
  },
  RouterView: {
    template: '<div class="router-view-stub"></div>',
  },
}))

// Mock vue-i18n
const mockLocale = ref('en')
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'app.title': 'TSS PPM',
        'nav.dashboard': 'Dashboard',
        'nav.team': 'Team Dashboard',
      }
      return messages[key] || key
    },
    locale: mockLocale,
  }),
}))

// Mock auth API
vi.mock('../api/auth', () => ({
  getCurrentUser: vi.fn(),
}))

// Mock useSidebar composable
vi.mock('../composables/useSidebar', () => ({
  useSidebar: () => ({
    sidebarMode: ref('expanded'),
    isExpanded: ref(true),
    isCollapsed: ref(false),
    isHidden: ref(false),
    isVisible: ref(true),
    showHamburger: ref(false),
    viewportWidth: ref(1200),
    toggle: vi.fn(),
    close: vi.fn(),
    open: vi.fn(),
  }),
  _resetSidebarState: vi.fn(),
}))

import * as auth from '../api/auth'

describe('App Navigation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRoute.value = { path: '/' }
    mockLocale.value = 'en'
  })

  function createWrapper() {
    return mount(App, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a :href="to" class="router-link"><slot /></a>',
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

      expect(wrapper.text()).toContain('Team Dashboard')
    })

    it('should NOT show Team link for employees without manager role', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue({
        email: 'employee@example.com',
        name: 'Test Employee',
        roles: ['employee'],
      })

      const wrapper = createWrapper()

      expect(wrapper.text()).not.toContain('Team Dashboard')
    })

    it('should handle null user gracefully', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue(null)

      const wrapper = createWrapper()

      // Should still render without crashing
      expect(wrapper.text()).toContain('Dashboard')
      expect(wrapper.text()).not.toContain('Team Dashboard')
    })

    it('should handle user without roles array', () => {
      vi.mocked(auth.getCurrentUser).mockReturnValue({
        email: 'user@example.com',
        name: 'Test User',
        roles: undefined as unknown as string[],
      })

      const wrapper = createWrapper()

      expect(wrapper.text()).not.toContain('Team Dashboard')
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
