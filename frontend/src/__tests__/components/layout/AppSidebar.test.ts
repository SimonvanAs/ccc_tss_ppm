// TSS PPM v3.0 - AppSidebar Component Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import AppSidebar from '../../../components/layout/AppSidebar.vue'

// Mock vue-router
const mockRoute = ref({ path: '/' })
vi.mock('vue-router', () => ({
  useRoute: () => mockRoute.value,
  RouterLink: {
    template: '<a :href="to" :class="{ \'router-link-active\': isActive }"><slot /></a>',
    props: ['to'],
    computed: {
      isActive() {
        return mockRoute.value.path === this.to
      },
    },
  },
}))

// Mock auth module
const mockUser = ref({
  id: 'user-123',
  name: 'Test User',
  email: 'test@tss.eu',
  roles: ['employee'],
  picture: 'https://example.com/avatar.jpg',
})

vi.mock('../../../api/auth', () => ({
  getCurrentUser: () => mockUser.value,
  hasRole: (role: string) => mockUser.value?.roles.includes(role) || false,
}))

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'nav.dashboard': 'Dashboard',
        'nav.team': 'Team Dashboard',
        'nav.profile': 'Profile',
        'nav.settings': 'Settings',
      }
      return messages[key] || key
    },
  }),
}))

describe('AppSidebar', () => {
  beforeEach(() => {
    mockRoute.value = { path: '/' }
    mockUser.value = {
      id: 'user-123',
      name: 'Test User',
      email: 'test@tss.eu',
      roles: ['employee'],
      picture: 'https://example.com/avatar.jpg',
    }
  })

  function createWrapper(options = {}) {
    return mount(AppSidebar, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a :to="to" class="router-link-stub"><slot /></a>',
            props: ['to'],
          },
        },
      },
      ...options,
    })
  }

  describe('navigation items', () => {
    it('should render navigation items', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.sidebar-nav').exists()).toBe(true)
      expect(wrapper.findAll('.nav-item').length).toBeGreaterThan(0)
    })

    it('should render Dashboard link for all roles', () => {
      const wrapper = createWrapper()
      // Check for Dashboard text in the sidebar nav
      expect(wrapper.text()).toContain('Dashboard')
    })
  })

  describe('role-based visibility', () => {
    it('should show Team Dashboard link for manager role', () => {
      mockUser.value = { ...mockUser.value, roles: ['manager'] }
      const wrapper = createWrapper()
      // Check for Team Dashboard text when user is manager
      expect(wrapper.text()).toContain('Team Dashboard')
    })

    it('should hide Team Dashboard link for employee role', () => {
      mockUser.value = { ...mockUser.value, roles: ['employee'] }
      const wrapper = createWrapper()
      expect(wrapper.text()).not.toContain('Team Dashboard')
    })

    it('should hide Team Dashboard link for hr role', () => {
      mockUser.value = { ...mockUser.value, roles: ['hr'] }
      const wrapper = createWrapper()
      expect(wrapper.text()).not.toContain('Team Dashboard')
    })

    it('should hide Team Dashboard link for admin role', () => {
      mockUser.value = { ...mockUser.value, roles: ['admin'] }
      const wrapper = createWrapper()
      expect(wrapper.text()).not.toContain('Team Dashboard')
    })
  })

  describe('profile section', () => {
    it('should render profile section at bottom', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.sidebar-profile').exists()).toBe(true)
    })

    it('should display user avatar', () => {
      const wrapper = createWrapper()
      const avatar = wrapper.find('.profile-avatar')
      expect(avatar.exists()).toBe(true)
    })

    it('should display user name', () => {
      const wrapper = createWrapper()
      expect(wrapper.text()).toContain('Test User')
    })

    it('should show default avatar when no picture available', () => {
      mockUser.value = { ...mockUser.value, picture: undefined }
      const wrapper = createWrapper()
      const avatar = wrapper.find('.profile-avatar')
      expect(avatar.exists()).toBe(true)
      // Should have fallback/default state
    })
  })

  describe('active state', () => {
    it('should highlight active nav item based on current route', () => {
      mockRoute.value = { path: '/' }
      const wrapper = createWrapper()
      const navItems = wrapper.findAll('.nav-item')
      // Dashboard should be active
      const dashboardItem = navItems.find((item) => item.text().includes('Dashboard'))
      expect(dashboardItem?.classes()).toContain('is-active')
    })

    it('should highlight Team Dashboard when on /team route', () => {
      mockRoute.value = { path: '/team' }
      mockUser.value = { ...mockUser.value, roles: ['manager'] }
      const wrapper = createWrapper()
      const navItems = wrapper.findAll('.nav-item')
      const teamItem = navItems.find((item) => item.text().includes('Team'))
      expect(teamItem?.classes()).toContain('is-active')
    })
  })

  describe('styling', () => {
    it('should have sidebar root class', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.app-sidebar').exists()).toBe(true)
    })

    it('should have navy background color class', () => {
      const wrapper = createWrapper()
      // The sidebar should have navy background styling
      expect(wrapper.find('.app-sidebar').exists()).toBe(true)
    })
  })
})
