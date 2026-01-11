// TSS PPM v3.0 - CalibrationNineGrid Tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import CalibrationNineGrid from '../../components/calibration/CalibrationNineGrid.vue'
import type { CalibrationReview } from '../../api/calibration'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const messages: Record<string, string> = {
        'calibration.grid.title': 'Calibration Grid',
        'calibration.grid.whatAxis': 'WHAT',
        'calibration.grid.howAxis': 'HOW',
        'calibration.grid.noReviews': 'No reviews to display',
        'calibration.grid.clickToSelect': 'Click to select',
        'calibration.grid.employeesInCell': '{count} employees',
        'calibration.grid.whatScore': 'WHAT Score',
        'calibration.grid.howScore': 'HOW Score',
        'calibration.grid.manager': 'Manager',
        'calibration.grid.veto': 'VETO Active',
      }
      return messages[key] || key
    },
  }),
}))

function createMockReview(overrides: Partial<CalibrationReview> = {}): CalibrationReview {
  return {
    review_id: 'review-1',
    employee_id: 'emp-1',
    employee_name: 'John Doe',
    employee_email: 'john@example.com',
    what_score: 2.5,
    how_score: 2.0,
    grid_position_what: 2,
    grid_position_how: 2,
    what_veto_active: false,
    how_veto_active: false,
    review_status: 'SIGNED',
    manager_first_name: 'Jane',
    manager_last_name: 'Smith',
    ...overrides,
  }
}

describe('CalibrationNineGrid', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  function createWrapper(props: { reviews: CalibrationReview[]; selectedReviewId?: string }) {
    return mount(CalibrationNineGrid, {
      props,
    })
  }

  describe('grid rendering', () => {
    it('should render 3x3 grid structure', () => {
      const wrapper = createWrapper({ reviews: [] })

      const cells = wrapper.findAll('.grid-cell')
      expect(cells).toHaveLength(9)
    })

    it('should render WHAT axis label', () => {
      const wrapper = createWrapper({ reviews: [] })

      expect(wrapper.text()).toContain('WHAT')
    })

    it('should render HOW axis label', () => {
      const wrapper = createWrapper({ reviews: [] })

      expect(wrapper.text()).toContain('HOW')
    })

    it('should render row labels (3, 2, 1)', () => {
      const wrapper = createWrapper({ reviews: [] })

      const rowLabels = wrapper.findAll('.row-label')
      expect(rowLabels).toHaveLength(3)
      expect(rowLabels[0].text()).toBe('3')
      expect(rowLabels[1].text()).toBe('2')
      expect(rowLabels[2].text()).toBe('1')
    })

    it('should render column labels (1, 2, 3)', () => {
      const wrapper = createWrapper({ reviews: [] })

      const colLabels = wrapper.findAll('.col-label')
      expect(colLabels).toHaveLength(3)
      expect(colLabels[0].text()).toBe('1')
      expect(colLabels[1].text()).toBe('2')
      expect(colLabels[2].text()).toBe('3')
    })
  })

  describe('employee markers', () => {
    it('should display employee markers for reviews with scores', () => {
      const reviews = [
        createMockReview({ review_id: 'r1', grid_position_what: 2, grid_position_how: 2 }),
      ]
      const wrapper = createWrapper({ reviews })

      const markers = wrapper.findAll('.employee-marker')
      expect(markers).toHaveLength(1)
    })

    it('should display multiple employee markers in same cell', () => {
      const reviews = [
        createMockReview({ review_id: 'r1', employee_name: 'John', grid_position_what: 2, grid_position_how: 2 }),
        createMockReview({ review_id: 'r2', employee_name: 'Jane', grid_position_what: 2, grid_position_how: 2 }),
      ]
      const wrapper = createWrapper({ reviews })

      const cell = wrapper.find('.grid-cell[data-what="2"][data-how="2"]')
      const markers = cell.findAll('.employee-marker')
      expect(markers).toHaveLength(2)
    })

    it('should show employee initials on markers', () => {
      const reviews = [
        createMockReview({ employee_name: 'John Doe' }),
      ]
      const wrapper = createWrapper({ reviews })

      const marker = wrapper.find('.marker-initials')
      expect(marker.text()).toBe('JD')
    })

    it('should not display markers for reviews without grid positions', () => {
      const reviews = [
        createMockReview({ grid_position_what: null, grid_position_how: null }),
      ]
      const wrapper = createWrapper({ reviews })

      const markers = wrapper.findAll('.employee-marker')
      expect(markers).toHaveLength(0)
    })
  })

  describe('cell coloring', () => {
    it('should apply dark-green color to cell (3,3)', () => {
      const reviews = [
        createMockReview({ grid_position_what: 3, grid_position_how: 3 }),
      ]
      const wrapper = createWrapper({ reviews })

      const cell = wrapper.find('.grid-cell[data-what="3"][data-how="3"]')
      expect(cell.classes()).toContain('color-dark-green')
    })

    it('should apply green color to cells with sum >= 5', () => {
      const reviews = [
        createMockReview({ grid_position_what: 3, grid_position_how: 2 }),
      ]
      const wrapper = createWrapper({ reviews })

      const cell = wrapper.find('.grid-cell[data-what="3"][data-how="2"]')
      expect(cell.classes()).toContain('color-green')
    })

    it('should apply red color to cell (1,1)', () => {
      const wrapper = createWrapper({ reviews: [] })

      const cell = wrapper.find('.grid-cell[data-what="1"][data-how="1"]')
      expect(cell.classes()).toContain('color-red')
    })
  })

  describe('employee selection', () => {
    it('should emit select event when marker clicked', async () => {
      const review = createMockReview()
      const wrapper = createWrapper({ reviews: [review] })

      const marker = wrapper.find('.employee-marker')
      await marker.trigger('click')

      expect(wrapper.emitted('select')).toHaveLength(1)
      expect(wrapper.emitted('select')![0]).toEqual([review])
    })

    it('should highlight selected employee marker', () => {
      const review = createMockReview({ review_id: 'selected-review' })
      const wrapper = createWrapper({
        reviews: [review],
        selectedReviewId: 'selected-review',
      })

      const marker = wrapper.find('.employee-marker')
      expect(marker.classes()).toContain('selected')
    })

    it('should emit select on keyboard Enter', async () => {
      const review = createMockReview()
      const wrapper = createWrapper({ reviews: [review] })

      const marker = wrapper.find('.employee-marker')
      await marker.trigger('keydown', { key: 'Enter' })

      expect(wrapper.emitted('select')).toHaveLength(1)
    })

    it('should emit select on keyboard Space', async () => {
      const review = createMockReview()
      const wrapper = createWrapper({ reviews: [review] })

      const marker = wrapper.find('.employee-marker')
      await marker.trigger('keydown', { key: ' ' })

      expect(wrapper.emitted('select')).toHaveLength(1)
    })
  })

  describe('hover tooltip', () => {
    it('should show tooltip on marker hover', async () => {
      const review = createMockReview({ employee_name: 'John Doe' })
      const wrapper = createWrapper({ reviews: [review] })

      const marker = wrapper.find('.employee-marker')
      await marker.trigger('mouseenter')

      const tooltip = wrapper.find('.employee-tooltip')
      expect(tooltip.exists()).toBe(true)
      expect(tooltip.text()).toContain('John Doe')
    })

    it('should display scores in tooltip', async () => {
      const review = createMockReview({ what_score: 2.5, how_score: 2.0 })
      const wrapper = createWrapper({ reviews: [review] })

      const marker = wrapper.find('.employee-marker')
      await marker.trigger('mouseenter')

      const tooltip = wrapper.find('.employee-tooltip')
      expect(tooltip.text()).toContain('2.5')
      expect(tooltip.text()).toContain('2.0')
    })

    it('should display manager name in tooltip', async () => {
      const review = createMockReview({
        manager_first_name: 'Jane',
        manager_last_name: 'Smith',
      })
      const wrapper = createWrapper({ reviews: [review] })

      const marker = wrapper.find('.employee-marker')
      await marker.trigger('mouseenter')

      const tooltip = wrapper.find('.employee-tooltip')
      expect(tooltip.text()).toContain('Jane Smith')
    })

    it('should hide tooltip on mouse leave', async () => {
      const review = createMockReview()
      const wrapper = createWrapper({ reviews: [review] })

      const marker = wrapper.find('.employee-marker')
      await marker.trigger('mouseenter')
      expect(wrapper.find('.employee-tooltip').exists()).toBe(true)

      await marker.trigger('mouseleave')
      expect(wrapper.find('.employee-tooltip').exists()).toBe(false)
    })
  })

  describe('veto indicator', () => {
    it('should show veto styling when what_veto_active', () => {
      const review = createMockReview({ what_veto_active: true })
      const wrapper = createWrapper({ reviews: [review] })

      const marker = wrapper.find('.employee-marker')
      expect(marker.classes()).toContain('veto-active')
    })

    it('should show veto styling when how_veto_active', () => {
      const review = createMockReview({ how_veto_active: true })
      const wrapper = createWrapper({ reviews: [review] })

      const marker = wrapper.find('.employee-marker')
      expect(marker.classes()).toContain('veto-active')
    })

    it('should display veto indicator in tooltip', async () => {
      const review = createMockReview({ what_veto_active: true })
      const wrapper = createWrapper({ reviews: [review] })

      const marker = wrapper.find('.employee-marker')
      await marker.trigger('mouseenter')

      const tooltip = wrapper.find('.employee-tooltip')
      expect(tooltip.text()).toContain('VETO')
    })
  })

  describe('cell count badge', () => {
    it('should show count badge when multiple employees in cell', () => {
      const reviews = [
        createMockReview({ review_id: 'r1', grid_position_what: 2, grid_position_how: 2 }),
        createMockReview({ review_id: 'r2', grid_position_what: 2, grid_position_how: 2 }),
        createMockReview({ review_id: 'r3', grid_position_what: 2, grid_position_how: 2 }),
      ]
      const wrapper = createWrapper({ reviews })

      const countBadge = wrapper.find('.cell-count')
      expect(countBadge.exists()).toBe(true)
      expect(countBadge.text()).toBe('3')
    })

    it('should not show count badge for single employee', () => {
      const reviews = [
        createMockReview({ grid_position_what: 2, grid_position_how: 2 }),
      ]
      const wrapper = createWrapper({ reviews })

      const countBadge = wrapper.find('.cell-count')
      expect(countBadge.exists()).toBe(false)
    })
  })

  describe('empty state', () => {
    it('should show empty message when no reviews', () => {
      const wrapper = createWrapper({ reviews: [] })

      expect(wrapper.text()).toContain('No reviews to display')
    })

    it('should show empty message when all reviews lack grid positions', () => {
      const reviews = [
        createMockReview({ grid_position_what: null, grid_position_how: null }),
      ]
      const wrapper = createWrapper({ reviews })

      expect(wrapper.text()).toContain('No reviews to display')
    })
  })

  describe('dense cell handling', () => {
    it('should limit visible markers based on maxMarkersPerCell prop', () => {
      const reviews = Array.from({ length: 10 }, (_, i) =>
        createMockReview({
          review_id: `r${i}`,
          employee_name: `Employee ${i}`,
          grid_position_what: 2,
          grid_position_how: 2,
        })
      )
      const wrapper = createWrapper({ reviews })

      const cell = wrapper.find('.grid-cell[data-what="2"][data-how="2"]')
      const markers = cell.findAll('.employee-marker')
      // Default max is 5
      expect(markers.length).toBeLessThanOrEqual(5)
    })

    it('should show overflow indicator for dense cells', () => {
      const reviews = Array.from({ length: 10 }, (_, i) =>
        createMockReview({
          review_id: `r${i}`,
          grid_position_what: 2,
          grid_position_how: 2,
        })
      )
      const wrapper = createWrapper({ reviews })

      const overflow = wrapper.find('.overflow-indicator')
      expect(overflow.exists()).toBe(true)
    })
  })

  describe('accessibility', () => {
    it('should have role="grid" on grid element', () => {
      const wrapper = createWrapper({ reviews: [] })

      const grid = wrapper.find('.grid')
      expect(grid.attributes('role')).toBe('grid')
    })

    it('should have role="gridcell" on cells', () => {
      const wrapper = createWrapper({ reviews: [] })

      const cell = wrapper.find('.grid-cell')
      expect(cell.attributes('role')).toBe('gridcell')
    })

    it('should have aria-label on markers', () => {
      const review = createMockReview({ employee_name: 'John Doe' })
      const wrapper = createWrapper({ reviews: [review] })

      const marker = wrapper.find('.employee-marker')
      expect(marker.attributes('aria-label')).toContain('John Doe')
    })

    it('should have tabindex on markers for keyboard navigation', () => {
      const review = createMockReview()
      const wrapper = createWrapper({ reviews: [review] })

      const marker = wrapper.find('.employee-marker')
      expect(marker.attributes('tabindex')).toBe('0')
    })
  })
})
