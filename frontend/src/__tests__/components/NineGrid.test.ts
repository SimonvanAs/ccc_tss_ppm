// TSS PPM v3.0 - NineGrid Component Tests
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import NineGrid from '../../components/review/NineGrid.vue'

describe('NineGrid', () => {
  describe('3x3 grid rendering', () => {
    it('should render a 3x3 grid with 9 cells', () => {
      const wrapper = mount(NineGrid)

      const cells = wrapper.findAll('.grid-cell')
      expect(cells).toHaveLength(9)
    })

    it('should render row labels (WHAT axis: 1, 2, 3)', () => {
      const wrapper = mount(NineGrid)

      const rowLabels = wrapper.findAll('.row-label')
      expect(rowLabels).toHaveLength(3)
      expect(rowLabels[0].text()).toBe('3')
      expect(rowLabels[1].text()).toBe('2')
      expect(rowLabels[2].text()).toBe('1')
    })

    it('should render column labels (HOW axis: 1, 2, 3)', () => {
      const wrapper = mount(NineGrid)

      const colLabels = wrapper.findAll('.col-label')
      expect(colLabels).toHaveLength(3)
      expect(colLabels[0].text()).toBe('1')
      expect(colLabels[1].text()).toBe('2')
      expect(colLabels[2].text()).toBe('3')
    })

    it('should render axis titles', () => {
      const wrapper = mount(NineGrid)

      expect(wrapper.text()).toContain('WHAT')
      expect(wrapper.text()).toContain('HOW')
    })
  })

  describe('position calculation', () => {
    it('should position marker in bottom-left for scores (1, 1)', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 1, howScore: 1 },
      })

      const marker = wrapper.find('.position-marker')
      expect(marker.exists()).toBe(true)

      // Check marker is in cell (1,1) - bottom-left
      const cell = wrapper.find('[data-what="1"][data-how="1"]')
      expect(cell.find('.position-marker').exists()).toBe(true)
    })

    it('should position marker in top-right for scores (3, 3)', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 3, howScore: 3 },
      })

      const cell = wrapper.find('[data-what="3"][data-how="3"]')
      expect(cell.find('.position-marker').exists()).toBe(true)
    })

    it('should position marker in center for scores (2, 2)', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 2, howScore: 2 },
      })

      const cell = wrapper.find('[data-what="2"][data-how="2"]')
      expect(cell.find('.position-marker').exists()).toBe(true)
    })

    it('should round scores to nearest integer for cell placement', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 2.4, howScore: 1.6 },
      })

      // 2.4 rounds to 2, 1.6 rounds to 2
      const cell = wrapper.find('[data-what="2"][data-how="2"]')
      expect(cell.find('.position-marker').exists()).toBe(true)
    })

    it('should clamp scores below 1 to 1', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 0.5, howScore: 0.8 },
      })

      const cell = wrapper.find('[data-what="1"][data-how="1"]')
      expect(cell.find('.position-marker').exists()).toBe(true)
    })

    it('should clamp scores above 3 to 3', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 3.5, howScore: 4 },
      })

      const cell = wrapper.find('[data-what="3"][data-how="3"]')
      expect(cell.find('.position-marker').exists()).toBe(true)
    })

    it('should not show marker when scores are null', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: null, howScore: null },
      })

      const marker = wrapper.find('.position-marker')
      expect(marker.exists()).toBe(false)
    })

    it('should not show marker when only whatScore is provided', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 2, howScore: null },
      })

      const marker = wrapper.find('.position-marker')
      expect(marker.exists()).toBe(false)
    })
  })

  describe('cell color coding', () => {
    it('should have red color for cell (1,1)', () => {
      const wrapper = mount(NineGrid)

      const cell = wrapper.find('[data-what="1"][data-how="1"]')
      expect(cell.classes()).toContain('color-red')
    })

    it('should have red color for cell (1,2)', () => {
      const wrapper = mount(NineGrid)

      const cell = wrapper.find('[data-what="1"][data-how="2"]')
      expect(cell.classes()).toContain('color-red')
    })

    it('should have red color for cell (2,1)', () => {
      const wrapper = mount(NineGrid)

      const cell = wrapper.find('[data-what="2"][data-how="1"]')
      expect(cell.classes()).toContain('color-red')
    })

    it('should have orange color for cell (1,3)', () => {
      const wrapper = mount(NineGrid)

      const cell = wrapper.find('[data-what="1"][data-how="3"]')
      expect(cell.classes()).toContain('color-orange')
    })

    it('should have orange color for cell (2,2)', () => {
      const wrapper = mount(NineGrid)

      const cell = wrapper.find('[data-what="2"][data-how="2"]')
      expect(cell.classes()).toContain('color-orange')
    })

    it('should have orange color for cell (3,1)', () => {
      const wrapper = mount(NineGrid)

      const cell = wrapper.find('[data-what="3"][data-how="1"]')
      expect(cell.classes()).toContain('color-orange')
    })

    it('should have green color for cell (2,3)', () => {
      const wrapper = mount(NineGrid)

      const cell = wrapper.find('[data-what="2"][data-how="3"]')
      expect(cell.classes()).toContain('color-green')
    })

    it('should have green color for cell (3,2)', () => {
      const wrapper = mount(NineGrid)

      const cell = wrapper.find('[data-what="3"][data-how="2"]')
      expect(cell.classes()).toContain('color-green')
    })

    it('should have dark-green color for cell (3,3)', () => {
      const wrapper = mount(NineGrid)

      const cell = wrapper.find('[data-what="3"][data-how="3"]')
      expect(cell.classes()).toContain('color-dark-green')
    })
  })

  describe('real-time position updates', () => {
    it('should update marker position when whatScore changes', async () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 1, howScore: 2 },
      })

      // Initially at (1, 2)
      let cell = wrapper.find('[data-what="1"][data-how="2"]')
      expect(cell.find('.position-marker').exists()).toBe(true)

      // Update whatScore to 3
      await wrapper.setProps({ whatScore: 3 })

      // Now at (3, 2)
      cell = wrapper.find('[data-what="3"][data-how="2"]')
      expect(cell.find('.position-marker').exists()).toBe(true)

      // Old cell should not have marker
      const oldCell = wrapper.find('[data-what="1"][data-how="2"]')
      expect(oldCell.find('.position-marker').exists()).toBe(false)
    })

    it('should update marker position when howScore changes', async () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 2, howScore: 1 },
      })

      // Initially at (2, 1)
      let cell = wrapper.find('[data-what="2"][data-how="1"]')
      expect(cell.find('.position-marker').exists()).toBe(true)

      // Update howScore to 3
      await wrapper.setProps({ howScore: 3 })

      // Now at (2, 3)
      cell = wrapper.find('[data-what="2"][data-how="3"]')
      expect(cell.find('.position-marker').exists()).toBe(true)
    })

    it('should remove marker when scores become null', async () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 2, howScore: 2 },
      })

      expect(wrapper.find('.position-marker').exists()).toBe(true)

      await wrapper.setProps({ whatScore: null, howScore: null })

      expect(wrapper.find('.position-marker').exists()).toBe(false)
    })
  })

  describe('VETO state display', () => {
    it('should show VETO indicator when vetoActive is true', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 1, howScore: 2, vetoActive: true },
      })

      expect(wrapper.find('.veto-indicator').exists()).toBe(true)
    })

    it('should highlight the (1, x) row when WHAT veto is active', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 1, howScore: 2, vetoActive: true, vetoType: 'SCF' },
      })

      // The marker should be in row 1 (WHAT score forced to 1)
      const cell = wrapper.find('[data-what="1"][data-how="2"]')
      expect(cell.find('.position-marker').exists()).toBe(true)
    })

    it('should highlight the (x, 1) column when HOW veto is active', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 2, howScore: 1, vetoActive: true, vetoType: 'COMPETENCY' },
      })

      // The marker should be in column 1 (HOW score forced to 1)
      const cell = wrapper.find('[data-what="2"][data-how="1"]')
      expect(cell.find('.position-marker').exists()).toBe(true)
    })
  })

  describe('accessibility', () => {
    it('should have appropriate ARIA labels', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 2, howScore: 3 },
      })

      expect(wrapper.find('[role="grid"]').exists()).toBe(true)
    })

    it('should have aria-label describing current position', () => {
      const wrapper = mount(NineGrid, {
        props: { whatScore: 2, howScore: 3 },
      })

      const grid = wrapper.find('[role="grid"]')
      expect(grid.attributes('aria-label')).toContain('WHAT: 2')
      expect(grid.attributes('aria-label')).toContain('HOW: 3')
    })
  })

  describe('compact mode', () => {
    it('should apply compact class when compact prop is true', () => {
      const wrapper = mount(NineGrid, {
        props: { compact: true },
      })

      expect(wrapper.find('.nine-grid').classes()).toContain('compact')
    })

    it('should hide axis labels in compact mode', () => {
      const wrapper = mount(NineGrid, {
        props: { compact: true },
      })

      expect(wrapper.find('.axis-title').exists()).toBe(false)
    })
  })
})
