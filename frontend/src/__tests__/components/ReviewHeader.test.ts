// TSS PPM v3.0 - ReviewHeader Component Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ref } from 'vue'
import ReviewHeader from '../../components/review/ReviewHeader.vue'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
    d: (date: Date) => date.toISOString().split('T')[0],
    locale: { value: 'en' },
  }),
}))

describe('ReviewHeader', () => {
  const baseProps = {
    reviewId: 'review-123',
    employeeName: 'John Doe',
    managerName: 'Jane Smith',
    reviewYear: 2026,
    status: 'DRAFT' as const,
    stage: 'GOAL_SETTING' as const,
    jobTitle: 'Software Developer',
    tovLevel: 'B',
    goalSettingCompletedAt: null as string | null,
    midYearCompletedAt: null as string | null,
    endYearCompletedAt: null as string | null,
  }

  describe('displaying employee name, manager name, review year', () => {
    it('should display employee name', () => {
      const wrapper = mount(ReviewHeader, {
        props: baseProps,
      })

      expect(wrapper.text()).toContain('John Doe')
    })

    it('should display manager name', () => {
      const wrapper = mount(ReviewHeader, {
        props: baseProps,
      })

      expect(wrapper.text()).toContain('Jane Smith')
    })

    it('should display review year', () => {
      const wrapper = mount(ReviewHeader, {
        props: baseProps,
      })

      expect(wrapper.text()).toContain('2026')
    })
  })

  describe('displaying stage dates', () => {
    it('should display "Pending" when goal_setting_completed_at is null', () => {
      const wrapper = mount(ReviewHeader, {
        props: {
          ...baseProps,
          goalSettingCompletedAt: null,
        },
      })

      expect(wrapper.text()).toContain('reviewHeader.pending')
    })

    it('should display formatted date when goal_setting_completed_at has value', () => {
      const wrapper = mount(ReviewHeader, {
        props: {
          ...baseProps,
          goalSettingCompletedAt: '2026-01-15T10:00:00Z',
        },
      })

      expect(wrapper.text()).toContain('2026-01-15')
    })

    it('should display mid_year_completed_at date when available', () => {
      const wrapper = mount(ReviewHeader, {
        props: {
          ...baseProps,
          midYearCompletedAt: '2026-06-20T14:30:00Z',
        },
      })

      expect(wrapper.text()).toContain('2026-06-20')
    })

    it('should display end_year_completed_at date when available', () => {
      const wrapper = mount(ReviewHeader, {
        props: {
          ...baseProps,
          endYearCompletedAt: '2026-12-10T09:00:00Z',
        },
      })

      expect(wrapper.text()).toContain('2026-12-10')
    })
  })

  describe('job title input', () => {
    it('should show editable job title input when in DRAFT status', () => {
      const wrapper = mount(ReviewHeader, {
        props: {
          ...baseProps,
          status: 'DRAFT',
        },
      })

      const input = wrapper.find('input[data-testid="job-title-input"]')
      expect(input.exists()).toBe(true)
      expect(input.attributes('disabled')).toBeUndefined()
    })

    it('should display current job title value', () => {
      const wrapper = mount(ReviewHeader, {
        props: {
          ...baseProps,
          jobTitle: 'Senior Engineer',
        },
      })

      const input = wrapper.find<HTMLInputElement>('input[data-testid="job-title-input"]')
      expect(input.element.value).toBe('Senior Engineer')
    })

    it('should emit update event when job title changes', async () => {
      const wrapper = mount(ReviewHeader, {
        props: baseProps,
      })

      const input = wrapper.find('input[data-testid="job-title-input"]')
      await input.setValue('Lead Developer')

      expect(wrapper.emitted('update:jobTitle')).toBeTruthy()
      expect(wrapper.emitted('update:jobTitle')![0]).toEqual(['Lead Developer'])
    })
  })

  describe('TOV level dropdown', () => {
    it('should show editable TOV level dropdown when in DRAFT status', () => {
      const wrapper = mount(ReviewHeader, {
        props: {
          ...baseProps,
          status: 'DRAFT',
        },
      })

      const select = wrapper.find('select[data-testid="tov-level-select"]')
      expect(select.exists()).toBe(true)
      expect(select.attributes('disabled')).toBeUndefined()
    })

    it('should display all TOV level options (A, B, C, D)', () => {
      const wrapper = mount(ReviewHeader, {
        props: baseProps,
      })

      const options = wrapper.findAll('select[data-testid="tov-level-select"] option')
      const values = options.map(o => o.element.value)
      expect(values).toContain('A')
      expect(values).toContain('B')
      expect(values).toContain('C')
      expect(values).toContain('D')
    })

    it('should display current TOV level value', () => {
      const wrapper = mount(ReviewHeader, {
        props: {
          ...baseProps,
          tovLevel: 'C',
        },
      })

      const select = wrapper.find<HTMLSelectElement>('select[data-testid="tov-level-select"]')
      expect(select.element.value).toBe('C')
    })

    it('should emit update event when TOV level changes', async () => {
      const wrapper = mount(ReviewHeader, {
        props: baseProps,
      })

      const select = wrapper.find('select[data-testid="tov-level-select"]')
      await select.setValue('D')

      expect(wrapper.emitted('update:tovLevel')).toBeTruthy()
      expect(wrapper.emitted('update:tovLevel')![0]).toEqual(['D'])
    })
  })

  describe('read-only mode after submission', () => {
    it('should disable job title input when status is PENDING_EMPLOYEE_SIGNATURE', () => {
      const wrapper = mount(ReviewHeader, {
        props: {
          ...baseProps,
          status: 'PENDING_EMPLOYEE_SIGNATURE',
        },
      })

      const input = wrapper.find('input[data-testid="job-title-input"]')
      expect(input.attributes('disabled')).toBeDefined()
    })

    it('should disable TOV level dropdown when status is PENDING_MANAGER_SIGNATURE', () => {
      const wrapper = mount(ReviewHeader, {
        props: {
          ...baseProps,
          status: 'PENDING_MANAGER_SIGNATURE',
        },
      })

      const select = wrapper.find('select[data-testid="tov-level-select"]')
      expect(select.attributes('disabled')).toBeDefined()
    })

    it('should disable inputs when status is SIGNED', () => {
      const wrapper = mount(ReviewHeader, {
        props: {
          ...baseProps,
          status: 'SIGNED',
        },
      })

      const input = wrapper.find('input[data-testid="job-title-input"]')
      const select = wrapper.find('select[data-testid="tov-level-select"]')
      expect(input.attributes('disabled')).toBeDefined()
      expect(select.attributes('disabled')).toBeDefined()
    })

    it('should disable inputs when status is ARCHIVED', () => {
      const wrapper = mount(ReviewHeader, {
        props: {
          ...baseProps,
          status: 'ARCHIVED',
        },
      })

      const input = wrapper.find('input[data-testid="job-title-input"]')
      const select = wrapper.find('select[data-testid="tov-level-select"]')
      expect(input.attributes('disabled')).toBeDefined()
      expect(select.attributes('disabled')).toBeDefined()
    })
  })

  describe('Card styling', () => {
    it('should render within a card container', () => {
      const wrapper = mount(ReviewHeader, {
        props: baseProps,
      })

      expect(wrapper.find('.review-header').exists()).toBe(true)
    })

    it('should have proper grid layout', () => {
      const wrapper = mount(ReviewHeader, {
        props: baseProps,
      })

      expect(wrapper.find('.review-header-grid').exists()).toBe(true)
    })
  })
})
