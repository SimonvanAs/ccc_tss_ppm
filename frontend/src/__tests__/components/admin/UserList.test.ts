// TSS PPM v3.0 - UserList Component Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ref } from 'vue'
import UserList from '../../../components/admin/UserList.vue'
import type { AdminUser } from '../../../api/admin'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'admin.users.title': 'User Management',
        'admin.users.search': 'Search users...',
        'admin.users.filterByRole': 'Filter by role',
        'admin.users.filterByStatus': 'Filter by status',
        'admin.users.allRoles': 'All roles',
        'admin.users.allStatuses': 'All statuses',
        'admin.users.active': 'Active',
        'admin.users.inactive': 'Inactive',
        'admin.users.name': 'Name',
        'admin.users.email': 'Email',
        'admin.users.roles': 'Roles',
        'admin.users.status': 'Status',
        'admin.users.actions': 'Actions',
        'admin.users.edit': 'Edit',
        'admin.users.deactivate': 'Deactivate',
        'admin.users.activate': 'Activate',
        'admin.users.noUsers': 'No users found',
        'admin.users.loading': 'Loading users...',
        'admin.users.previousPage': 'Previous',
        'admin.users.nextPage': 'Next',
        'admin.users.pageInfo': 'Page {page}',
        'roles.employee': 'Employee',
        'roles.manager': 'Manager',
        'roles.hr': 'HR',
        'roles.admin': 'Admin',
      }
      return translations[key] || key
    },
  }),
}))

const mockUsers: AdminUser[] = [
  {
    id: 'user-1',
    email: 'john.doe@tss.eu',
    first_name: 'John',
    last_name: 'Doe',
    enabled: true,
    roles: ['employee', 'manager'],
    function_title: 'Software Engineer',
    tov_level: 'B',
    manager_id: 'manager-1',
    opco_id: 'opco-1',
  },
  {
    id: 'user-2',
    email: 'jane.smith@tss.eu',
    first_name: 'Jane',
    last_name: 'Smith',
    enabled: true,
    roles: ['employee'],
    function_title: 'UX Designer',
    tov_level: 'C',
    manager_id: 'manager-1',
    opco_id: 'opco-1',
  },
  {
    id: 'user-3',
    email: 'bob.wilson@tss.eu',
    first_name: 'Bob',
    last_name: 'Wilson',
    enabled: false,
    roles: ['employee'],
    function_title: 'Product Manager',
    tov_level: 'A',
    manager_id: 'manager-2',
    opco_id: 'opco-1',
  },
]

describe('UserList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('user table rendering', () => {
    it('should render table with user data', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(3)
    })

    it('should display user name correctly', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const firstRow = wrapper.find('tbody tr')
      expect(firstRow.text()).toContain('John Doe')
    })

    it('should display user email', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const firstRow = wrapper.find('tbody tr')
      expect(firstRow.text()).toContain('john.doe@tss.eu')
    })

    it('should display user roles as badges', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const roleBadges = wrapper.findAll('.role-badge')
      expect(roleBadges.length).toBeGreaterThan(0)
    })

    it('should show active/inactive status', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const statusBadges = wrapper.findAll('.status-badge')
      expect(statusBadges.length).toBe(3)

      // First two users are active, third is inactive
      expect(statusBadges[0].classes()).toContain('status-active')
      expect(statusBadges[2].classes()).toContain('status-inactive')
    })

    it('should show loading state', () => {
      const wrapper = mount(UserList, {
        props: {
          users: [],
          loading: true,
        },
      })

      expect(wrapper.text()).toContain('Loading users...')
    })

    it('should show empty state when no users', () => {
      const wrapper = mount(UserList, {
        props: {
          users: [],
          loading: false,
        },
      })

      expect(wrapper.text()).toContain('No users found')
    })
  })

  describe('search functionality', () => {
    it('should render search input', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const searchInput = wrapper.find('input[type="search"]')
      expect(searchInput.exists()).toBe(true)
    })

    it('should emit search event on input after debounce', async () => {
      vi.useFakeTimers()

      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const searchInput = wrapper.find('input[type="search"]')
      await searchInput.setValue('john')

      // Advance past debounce timer
      vi.advanceTimersByTime(300)
      await flushPromises()

      expect(wrapper.emitted('search')).toBeTruthy()
      expect(wrapper.emitted('search')![0]).toEqual(['john'])

      vi.useRealTimers()
    })

    it('should debounce search input', async () => {
      vi.useFakeTimers()

      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const searchInput = wrapper.find('input[type="search"]')
      await searchInput.setValue('j')
      await searchInput.setValue('jo')
      await searchInput.setValue('joh')
      await searchInput.setValue('john')

      // Should not emit immediately
      expect(wrapper.emitted('search')?.length || 0).toBeLessThan(4)

      // Fast forward debounce timer
      vi.advanceTimersByTime(300)
      await flushPromises()

      // Should emit final value
      const searchEvents = wrapper.emitted('search')
      expect(searchEvents).toBeTruthy()

      vi.useRealTimers()
    })
  })

  describe('role filter dropdown', () => {
    it('should render role filter dropdown', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const roleFilter = wrapper.find('[data-testid="role-filter"]')
      expect(roleFilter.exists()).toBe(true)
    })

    it('should have role options', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const options = wrapper.findAll('[data-testid="role-filter"] option')
      expect(options.length).toBeGreaterThan(1) // At least "All" + roles
    })

    it('should emit filter event on role selection', async () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const roleFilter = wrapper.find('[data-testid="role-filter"]')
      await roleFilter.setValue('manager')

      expect(wrapper.emitted('filter-role')).toBeTruthy()
      expect(wrapper.emitted('filter-role')![0]).toEqual(['manager'])
    })
  })

  describe('status filter dropdown', () => {
    it('should render status filter dropdown', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const statusFilter = wrapper.find('[data-testid="status-filter"]')
      expect(statusFilter.exists()).toBe(true)
    })

    it('should have active/inactive options', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const options = wrapper.findAll('[data-testid="status-filter"] option')
      const optionTexts = options.map(o => o.text())

      expect(optionTexts).toContain('All statuses')
      expect(optionTexts).toContain('Active')
      expect(optionTexts).toContain('Inactive')
    })

    it('should emit filter event on status selection', async () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const statusFilter = wrapper.find('[data-testid="status-filter"]')
      await statusFilter.setValue('active')

      expect(wrapper.emitted('filter-status')).toBeTruthy()
      expect(wrapper.emitted('filter-status')![0]).toEqual([true])
    })
  })

  describe('pagination controls', () => {
    it('should render pagination when total exceeds page size', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
          currentPage: 1,
          totalPages: 3,
        },
      })

      const pagination = wrapper.find('.pagination')
      expect(pagination.exists()).toBe(true)
    })

    it('should not render pagination when single page', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
          currentPage: 1,
          totalPages: 1,
        },
      })

      const pagination = wrapper.find('.pagination')
      expect(pagination.exists()).toBe(false)
    })

    it('should disable previous button on first page', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
          currentPage: 1,
          totalPages: 3,
        },
      })

      const prevButton = wrapper.find('[data-testid="prev-page"]')
      expect(prevButton.attributes('disabled')).toBeDefined()
    })

    it('should disable next button on last page', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
          currentPage: 3,
          totalPages: 3,
        },
      })

      const nextButton = wrapper.find('[data-testid="next-page"]')
      expect(nextButton.attributes('disabled')).toBeDefined()
    })

    it('should emit page-change event on next click', async () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
          currentPage: 1,
          totalPages: 3,
        },
      })

      const nextButton = wrapper.find('[data-testid="next-page"]')
      await nextButton.trigger('click')

      expect(wrapper.emitted('page-change')).toBeTruthy()
      expect(wrapper.emitted('page-change')![0]).toEqual([2])
    })

    it('should emit page-change event on prev click', async () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
          currentPage: 2,
          totalPages: 3,
        },
      })

      const prevButton = wrapper.find('[data-testid="prev-page"]')
      await prevButton.trigger('click')

      expect(wrapper.emitted('page-change')).toBeTruthy()
      expect(wrapper.emitted('page-change')![0]).toEqual([1])
    })
  })

  describe('row actions', () => {
    it('should have edit button for each user', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const editButtons = wrapper.findAll('[data-testid="edit-user"]')
      expect(editButtons.length).toBe(3)
    })

    it('should emit edit event with user on click', async () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const editButton = wrapper.find('[data-testid="edit-user"]')
      await editButton.trigger('click')

      expect(wrapper.emitted('edit')).toBeTruthy()
      expect(wrapper.emitted('edit')![0]).toEqual([mockUsers[0]])
    })

    it('should show deactivate button for active users', () => {
      const wrapper = mount(UserList, {
        props: {
          users: [mockUsers[0]], // Active user
          loading: false,
        },
      })

      const deactivateButton = wrapper.find('[data-testid="toggle-status"]')
      expect(deactivateButton.text()).toContain('Deactivate')
    })

    it('should show activate button for inactive users', () => {
      const wrapper = mount(UserList, {
        props: {
          users: [mockUsers[2]], // Inactive user
          loading: false,
        },
      })

      const activateButton = wrapper.find('[data-testid="toggle-status"]')
      expect(activateButton.text()).toContain('Activate')
    })

    it('should emit toggle-status event on click', async () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
        },
      })

      const toggleButton = wrapper.find('[data-testid="toggle-status"]')
      await toggleButton.trigger('click')

      expect(wrapper.emitted('toggle-status')).toBeTruthy()
      expect(wrapper.emitted('toggle-status')![0]).toEqual([mockUsers[0]])
    })
  })

  describe('row selection', () => {
    it('should have checkbox for each row', () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
          selectable: true,
        },
      })

      const checkboxes = wrapper.findAll('input[type="checkbox"]')
      // Header checkbox + row checkboxes
      expect(checkboxes.length).toBe(4)
    })

    it('should emit select event when row checkbox toggled', async () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
          selectable: true,
          selectedIds: [],
        },
      })

      const rowCheckbox = wrapper.findAll('tbody input[type="checkbox"]')[0]
      await rowCheckbox.setValue(true)

      expect(wrapper.emitted('select')).toBeTruthy()
      expect(wrapper.emitted('select')![0]).toEqual([['user-1']])
    })

    it('should select all when header checkbox clicked', async () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
          selectable: true,
          selectedIds: [],
        },
      })

      const headerCheckbox = wrapper.find('thead input[type="checkbox"]')
      await headerCheckbox.setValue(true)

      expect(wrapper.emitted('select')).toBeTruthy()
      expect(wrapper.emitted('select')![0]).toEqual([['user-1', 'user-2', 'user-3']])
    })

    it('should deselect all when header checkbox unchecked', async () => {
      const wrapper = mount(UserList, {
        props: {
          users: mockUsers,
          loading: false,
          selectable: true,
          selectedIds: ['user-1', 'user-2', 'user-3'],
        },
      })

      const headerCheckbox = wrapper.find('thead input[type="checkbox"]')
      await headerCheckbox.setValue(false)

      expect(wrapper.emitted('select')).toBeTruthy()
      expect(wrapper.emitted('select')![0]).toEqual([[]])
    })
  })
})
