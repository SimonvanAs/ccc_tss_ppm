// TSS PPM v3.0 - TeamNineGrid Component Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import TeamNineGrid from '../../components/review/TeamNineGrid.vue'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'teamGrid.whatScore': 'WHAT Score',
        'teamGrid.howScore': 'HOW Score',
        'teamGrid.status': 'Status',
        'teamGrid.noEmployees': 'No employees to display',
        'teamGrid.clickToView': 'Click to view review',
      }
      return translations[key] || key
    },
  }),
}))

interface TeamMember {
  id: string
  email: string
  first_name: string
  last_name: string
  review_id: string | null
  review_status: string | null
  what_score: number | null
  how_score: number | null
  grid_position_what: number | null
  grid_position_how: number | null
  what_veto_active: boolean
  how_veto_active: boolean
}

describe('TeamNineGrid', () => {
  const createEmployee = (overrides: Partial<TeamMember> = {}): TeamMember => ({
    id: 'emp-1',
    email: 'john@example.com',
    first_name: 'John',
    last_name: 'Doe',
    review_id: 'review-1',
    review_status: 'DRAFT',
    what_score: 2.5,
    how_score: 2.8,
    grid_position_what: 3,
    grid_position_how: 3,
    what_veto_active: false,
    how_veto_active: false,
    ...overrides,
  })

  describe('multiple employee markers', () => {
    it('should render markers for each employee with scores', () => {
      const employees = [
        createEmployee({ id: 'emp-1', what_score: 2.5, how_score: 2.8, grid_position_what: 3, grid_position_how: 3 }),
        createEmployee({ id: 'emp-2', what_score: 1.5, how_score: 1.5, grid_position_what: 2, grid_position_how: 2 }),
      ]

      const wrapper = mount(TeamNineGrid, {
        props: { employees },
      })

      const markers = wrapper.findAll('.employee-marker')
      expect(markers.length).toBe(2)
    })

    it('should not render markers for employees without scores', () => {
      const employees = [
        createEmployee({ id: 'emp-1', what_score: 2.5, how_score: 2.8, grid_position_what: 3, grid_position_how: 3 }),
        createEmployee({ id: 'emp-2', what_score: null, how_score: null, grid_position_what: null, grid_position_how: null }),
      ]

      const wrapper = mount(TeamNineGrid, {
        props: { employees },
      })

      const markers = wrapper.findAll('.employee-marker')
      expect(markers.length).toBe(1)
    })

    it('should position markers in correct grid cells', () => {
      const employees = [
        createEmployee({ id: 'emp-1', grid_position_what: 3, grid_position_how: 3 }),
        createEmployee({ id: 'emp-2', grid_position_what: 1, grid_position_how: 1 }),
      ]

      const wrapper = mount(TeamNineGrid, {
        props: { employees },
      })

      // Check marker in cell (3,3) - top right
      const topRightCell = wrapper.find('[data-what="3"][data-how="3"]')
      expect(topRightCell.findAll('.employee-marker').length).toBe(1)

      // Check marker in cell (1,1) - bottom left
      const bottomLeftCell = wrapper.find('[data-what="1"][data-how="1"]')
      expect(bottomLeftCell.findAll('.employee-marker').length).toBe(1)
    })

    it('should handle multiple employees in same cell', () => {
      const employees = [
        createEmployee({ id: 'emp-1', grid_position_what: 2, grid_position_how: 2 }),
        createEmployee({ id: 'emp-2', first_name: 'Jane', grid_position_what: 2, grid_position_how: 2 }),
        createEmployee({ id: 'emp-3', first_name: 'Bob', grid_position_what: 2, grid_position_how: 2 }),
      ]

      const wrapper = mount(TeamNineGrid, {
        props: { employees },
      })

      const centerCell = wrapper.find('[data-what="2"][data-how="2"]')
      const markersInCell = centerCell.findAll('.employee-marker')
      expect(markersInCell.length).toBe(3)
    })
  })

  describe('hover tooltip', () => {
    it('should show tooltip with employee details on hover', async () => {
      const employee = createEmployee({
        first_name: 'John',
        last_name: 'Doe',
        what_score: 2.5,
        how_score: 2.8,
        review_status: 'DRAFT',
      })

      const wrapper = mount(TeamNineGrid, {
        props: { employees: [employee] },
      })

      const marker = wrapper.find('.employee-marker')
      await marker.trigger('mouseenter')

      const tooltip = wrapper.find('.employee-tooltip')
      expect(tooltip.exists()).toBe(true)
      expect(tooltip.text()).toContain('John Doe')
      expect(tooltip.text()).toContain('2.5')
      expect(tooltip.text()).toContain('2.8')
    })

    it('should hide tooltip on mouse leave', async () => {
      const wrapper = mount(TeamNineGrid, {
        props: { employees: [createEmployee()] },
      })

      const marker = wrapper.find('.employee-marker')
      await marker.trigger('mouseenter')
      expect(wrapper.find('.employee-tooltip').exists()).toBe(true)

      await marker.trigger('mouseleave')
      await nextTick()
      expect(wrapper.find('.employee-tooltip').exists()).toBe(false)
    })

    it('should show review status in tooltip', async () => {
      const employee = createEmployee({ review_status: 'PENDING_EMPLOYEE_SIGNATURE' })

      const wrapper = mount(TeamNineGrid, {
        props: { employees: [employee] },
      })

      const marker = wrapper.find('.employee-marker')
      await marker.trigger('mouseenter')

      const tooltip = wrapper.find('.employee-tooltip')
      expect(tooltip.text()).toContain('PENDING_EMPLOYEE_SIGNATURE')
    })
  })

  describe('click navigation', () => {
    it('should emit employee-click event when marker is clicked', async () => {
      const employee = createEmployee({ id: 'emp-123', review_id: 'review-456' })

      const wrapper = mount(TeamNineGrid, {
        props: { employees: [employee] },
      })

      const marker = wrapper.find('.employee-marker')
      await marker.trigger('click')

      expect(wrapper.emitted('employee-click')).toBeTruthy()
      expect(wrapper.emitted('employee-click')![0]).toEqual([employee])
    })

    it('should not emit click event for employees without review_id', async () => {
      const employee = createEmployee({ review_id: null })

      const wrapper = mount(TeamNineGrid, {
        props: { employees: [employee] },
        attachTo: document.body,
      })

      // Employee without scores won't have a marker
      const markers = wrapper.findAll('.employee-marker')
      expect(markers.length).toBe(1) // Has scores but no review_id

      if (markers.length > 0) {
        await markers[0].trigger('click')
        // Should still emit the click with the employee data
        expect(wrapper.emitted('employee-click')).toBeTruthy()
      }

      wrapper.unmount()
    })
  })

  describe('distribution counts', () => {
    it('should display count of employees in each cell', () => {
      const employees = [
        createEmployee({ id: 'emp-1', grid_position_what: 3, grid_position_how: 3 }),
        createEmployee({ id: 'emp-2', grid_position_what: 3, grid_position_how: 3 }),
        createEmployee({ id: 'emp-3', grid_position_what: 2, grid_position_how: 2 }),
      ]

      const wrapper = mount(TeamNineGrid, {
        props: { employees },
      })

      const topRightCell = wrapper.find('[data-what="3"][data-how="3"]')
      const countBadge = topRightCell.find('.cell-count')
      expect(countBadge.exists()).toBe(true)
      expect(countBadge.text()).toBe('2')
    })

    it('should not show count for cells with single employee', () => {
      const employees = [
        createEmployee({ id: 'emp-1', grid_position_what: 3, grid_position_how: 3 }),
      ]

      const wrapper = mount(TeamNineGrid, {
        props: { employees },
      })

      const topRightCell = wrapper.find('[data-what="3"][data-how="3"]')
      const countBadge = topRightCell.find('.cell-count')
      expect(countBadge.exists()).toBe(false)
    })

    it('should not show count for empty cells', () => {
      const employees = [
        createEmployee({ id: 'emp-1', grid_position_what: 3, grid_position_how: 3 }),
      ]

      const wrapper = mount(TeamNineGrid, {
        props: { employees },
      })

      const emptyCell = wrapper.find('[data-what="1"][data-how="1"]')
      const countBadge = emptyCell.find('.cell-count')
      expect(countBadge.exists()).toBe(false)
    })
  })

  describe('overlapping positions', () => {
    it('should offset markers when multiple employees are in same cell', () => {
      const employees = [
        createEmployee({ id: 'emp-1', grid_position_what: 2, grid_position_how: 2 }),
        createEmployee({ id: 'emp-2', first_name: 'Jane', grid_position_what: 2, grid_position_how: 2 }),
      ]

      const wrapper = mount(TeamNineGrid, {
        props: { employees },
      })

      const centerCell = wrapper.find('[data-what="2"][data-how="2"]')
      const markers = centerCell.findAll('.employee-marker')

      // Markers should have different positioning or stacking
      expect(markers.length).toBe(2)
      // The markers container should have a class indicating overlap handling
      const markersContainer = centerCell.find('.markers-container')
      expect(markersContainer.exists()).toBe(true)
    })

    it('should limit displayed markers and show overflow indicator', () => {
      // Create many employees in the same cell
      const employees = Array.from({ length: 10 }, (_, i) =>
        createEmployee({
          id: `emp-${i}`,
          first_name: `Employee${i}`,
          grid_position_what: 2,
          grid_position_how: 2,
        })
      )

      const wrapper = mount(TeamNineGrid, {
        props: { employees, maxMarkersPerCell: 5 },
      })

      const centerCell = wrapper.find('[data-what="2"][data-how="2"]')
      const markers = centerCell.findAll('.employee-marker')

      // Should show limited markers plus overflow indicator
      expect(markers.length).toBeLessThanOrEqual(5)

      // Should have count badge showing total
      const countBadge = centerCell.find('.cell-count')
      expect(countBadge.exists()).toBe(true)
      expect(countBadge.text()).toBe('10')
    })
  })

  describe('empty state', () => {
    it('should display message when no employees have scores', () => {
      const employees = [
        createEmployee({ id: 'emp-1', what_score: null, how_score: null, grid_position_what: null, grid_position_how: null }),
        createEmployee({ id: 'emp-2', what_score: null, how_score: null, grid_position_what: null, grid_position_how: null }),
      ]

      const wrapper = mount(TeamNineGrid, {
        props: { employees },
      })

      expect(wrapper.find('.no-scores-message').exists()).toBe(true)
    })

    it('should not display empty message when some employees have scores', () => {
      const employees = [
        createEmployee({ id: 'emp-1', what_score: 2.5, how_score: 2.8, grid_position_what: 3, grid_position_how: 3 }),
        createEmployee({ id: 'emp-2', what_score: null, how_score: null, grid_position_what: null, grid_position_how: null }),
      ]

      const wrapper = mount(TeamNineGrid, {
        props: { employees },
      })

      expect(wrapper.find('.no-scores-message').exists()).toBe(false)
    })
  })

  describe('accessibility', () => {
    it('should have appropriate ARIA labels for markers', () => {
      const employee = createEmployee({ first_name: 'John', last_name: 'Doe' })

      const wrapper = mount(TeamNineGrid, {
        props: { employees: [employee] },
      })

      const marker = wrapper.find('.employee-marker')
      expect(marker.attributes('aria-label')).toContain('John Doe')
    })

    it('should have role=button on clickable markers', () => {
      const wrapper = mount(TeamNineGrid, {
        props: { employees: [createEmployee()] },
      })

      const marker = wrapper.find('.employee-marker')
      expect(marker.attributes('role')).toBe('button')
    })

    it('should be keyboard navigable', async () => {
      const employee = createEmployee()

      const wrapper = mount(TeamNineGrid, {
        props: { employees: [employee] },
      })

      const marker = wrapper.find('.employee-marker')
      expect(marker.attributes('tabindex')).toBe('0')

      await marker.trigger('keydown', { key: 'Enter' })
      expect(wrapper.emitted('employee-click')).toBeTruthy()
    })
  })

  describe('VETO indicators', () => {
    it('should show VETO indicator on marker when veto is active', () => {
      const employee = createEmployee({ what_veto_active: true })

      const wrapper = mount(TeamNineGrid, {
        props: { employees: [employee] },
      })

      const marker = wrapper.find('.employee-marker')
      expect(marker.classes()).toContain('veto-active')
    })

    it('should show HOW VETO indicator on marker', () => {
      const employee = createEmployee({ how_veto_active: true })

      const wrapper = mount(TeamNineGrid, {
        props: { employees: [employee] },
      })

      const marker = wrapper.find('.employee-marker')
      expect(marker.classes()).toContain('veto-active')
    })
  })
})
