// TSS PPM v3.0 - AdminView Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ref } from 'vue'
import AdminView from '../../views/AdminView.vue'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'admin.pageTitle': 'Admin Settings',
        'admin.pageSubtitle': 'Manage users, settings, and system configuration',
        'admin.tabs.users': 'Users',
        'admin.tabs.opcoSettings': 'OpCo Settings',
        'admin.tabs.businessUnits': 'Business Units',
        'admin.tabs.system': 'System',
        'admin.tabs.auditLogs': 'Audit Logs',
        'admin.unauthorized': 'You are not authorized to access this page',
        'admin.loading': 'Loading...',
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
  useRoute: () => ({
    query: {},
  }),
}))

// Mock auth module
const mockUser = ref({
  id: 'user-123',
  name: 'Admin User',
  email: 'admin@tss.eu',
  roles: ['admin'],
})

vi.mock('../../api/auth', () => ({
  getCurrentUser: () => mockUser.value,
  hasRole: (role: string) => mockUser.value?.roles.includes(role) || false,
}))

describe('AdminView', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    mockPush.mockReset()
    mockUser.value = {
      id: 'user-123',
      name: 'Admin User',
      email: 'admin@tss.eu',
      roles: ['admin'],
    }
  })

  function createWrapper() {
    return mount(AdminView, {
      global: {
        stubs: {
          UserList: { template: '<div class="user-list-stub">User List</div>' },
          OpCoSettingsForm: { template: '<div class="opco-settings-stub">OpCo Settings</div>' },
          BusinessUnitList: { template: '<div class="business-unit-list-stub">Business Units</div>' },
          SystemHealthPanel: { template: '<div class="system-health-stub">System Health</div>' },
          AuditLogList: { template: '<div class="audit-log-list-stub">Audit Logs</div>' },
        },
      },
    })
  }

  describe('authorization', () => {
    it('should render admin view for admin role', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.admin-view').exists()).toBe(true)
      expect(wrapper.text()).toContain('Admin Settings')
    })

    it('should show unauthorized message for non-admin roles', async () => {
      mockUser.value = { ...mockUser.value, roles: ['employee'] }
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('You are not authorized')
    })

    it('should show unauthorized message for manager role', async () => {
      mockUser.value = { ...mockUser.value, roles: ['manager'] }
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('You are not authorized')
    })

    it('should show unauthorized message for hr role', async () => {
      mockUser.value = { ...mockUser.value, roles: ['hr'] }
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('You are not authorized')
    })

    it('should allow access when admin role is among multiple roles', async () => {
      mockUser.value = { ...mockUser.value, roles: ['employee', 'admin'] }
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.admin-view').exists()).toBe(true)
    })
  })

  describe('tab navigation', () => {
    it('should render all five tabs', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const tabs = wrapper.findAll('.tab-button')
      expect(tabs).toHaveLength(5)
    })

    it('should show Users tab by default', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const activeTab = wrapper.find('.tab-button.is-active')
      expect(activeTab.text()).toBe('Users')
    })

    it('should display Users tab content by default', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.user-list-stub').exists()).toBe(true)
    })

    it('should switch to OpCo Settings tab when clicked', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const tabs = wrapper.findAll('.tab-button')
      const opcoTab = tabs.find((tab) => tab.text() === 'OpCo Settings')
      await opcoTab?.trigger('click')

      expect(opcoTab?.classes()).toContain('is-active')
      expect(wrapper.find('.opco-settings-stub').exists()).toBe(true)
    })

    it('should switch to Business Units tab when clicked', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const tabs = wrapper.findAll('.tab-button')
      const buTab = tabs.find((tab) => tab.text() === 'Business Units')
      await buTab?.trigger('click')

      expect(buTab?.classes()).toContain('is-active')
      expect(wrapper.find('.business-unit-list-stub').exists()).toBe(true)
    })

    it('should switch to System tab when clicked', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const tabs = wrapper.findAll('.tab-button')
      const systemTab = tabs.find((tab) => tab.text() === 'System')
      await systemTab?.trigger('click')

      expect(systemTab?.classes()).toContain('is-active')
      expect(wrapper.find('.system-health-stub').exists()).toBe(true)
    })

    it('should switch to Audit Logs tab when clicked', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const tabs = wrapper.findAll('.tab-button')
      const auditTab = tabs.find((tab) => tab.text() === 'Audit Logs')
      await auditTab?.trigger('click')

      expect(auditTab?.classes()).toContain('is-active')
      expect(wrapper.find('.audit-log-list-stub').exists()).toBe(true)
    })
  })

  describe('page structure', () => {
    it('should display page title', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('Admin Settings')
    })

    it('should display page subtitle', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.text()).toContain('Manage users, settings, and system configuration')
    })

    it('should have tab navigation section', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.tab-navigation').exists()).toBe(true)
    })

    it('should have tab content section', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      expect(wrapper.find('.tab-content').exists()).toBe(true)
    })
  })

  describe('accessibility', () => {
    it('should have role="tablist" on tab navigation', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const tabNav = wrapper.find('.tab-navigation')
      expect(tabNav.attributes('role')).toBe('tablist')
    })

    it('should have role="tab" on tab buttons', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const tabs = wrapper.findAll('.tab-button')
      tabs.forEach((tab) => {
        expect(tab.attributes('role')).toBe('tab')
      })
    })

    it('should have aria-selected on active tab', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const activeTab = wrapper.find('.tab-button.is-active')
      expect(activeTab.attributes('aria-selected')).toBe('true')
    })

    it('should have role="tabpanel" on content area', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      const content = wrapper.find('.tab-content')
      expect(content.attributes('role')).toBe('tabpanel')
    })
  })
})
