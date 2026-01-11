// TSS PPM v3.0 - useSidebar Composable Tests
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { nextTick } from 'vue'
import { useSidebar, _resetSidebarState } from '../../composables/useSidebar'

describe('useSidebar', () => {
  let originalInnerWidth: number

  beforeEach(() => {
    originalInnerWidth = window.innerWidth
    _resetSidebarState()
  })

  afterEach(() => {
    // Restore original width
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    })
    _resetSidebarState()
  })

  function setViewportWidth(width: number) {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: width,
    })
    // Reset state after changing viewport to simulate real behavior
    _resetSidebarState()
  }

  describe('desktop viewport (≥1024px)', () => {
    it('should have sidebar expanded on desktop', () => {
      setViewportWidth(1024)
      const { isExpanded, isVisible } = useSidebar()
      expect(isExpanded.value).toBe(true)
      expect(isVisible.value).toBe(true)
    })

    it('should not show hamburger button on desktop', () => {
      setViewportWidth(1200)
      const { showHamburger } = useSidebar()
      expect(showHamburger.value).toBe(false)
    })

    it('should have sidebar mode as "expanded" on desktop', () => {
      setViewportWidth(1024)
      const { sidebarMode } = useSidebar()
      expect(sidebarMode.value).toBe('expanded')
    })
  })

  describe('tablet viewport (768px-1023px)', () => {
    it('should have sidebar collapsed on tablet', () => {
      setViewportWidth(800)
      const { isExpanded, isCollapsed } = useSidebar()
      expect(isExpanded.value).toBe(false)
      expect(isCollapsed.value).toBe(true)
    })

    it('should show hamburger button on tablet', () => {
      setViewportWidth(800)
      const { showHamburger } = useSidebar()
      expect(showHamburger.value).toBe(true)
    })

    it('should have sidebar mode as "collapsed" on tablet', () => {
      setViewportWidth(900)
      const { sidebarMode } = useSidebar()
      expect(sidebarMode.value).toBe('collapsed')
    })

    it('should still be visible when collapsed', () => {
      setViewportWidth(800)
      const { isVisible } = useSidebar()
      expect(isVisible.value).toBe(true)
    })
  })

  describe('mobile viewport (<768px)', () => {
    it('should have sidebar hidden on mobile', () => {
      setViewportWidth(500)
      const { isVisible, isHidden } = useSidebar()
      expect(isVisible.value).toBe(false)
      expect(isHidden.value).toBe(true)
    })

    it('should show hamburger button on mobile', () => {
      setViewportWidth(500)
      const { showHamburger } = useSidebar()
      expect(showHamburger.value).toBe(true)
    })

    it('should have sidebar mode as "hidden" on mobile', () => {
      setViewportWidth(400)
      const { sidebarMode } = useSidebar()
      expect(sidebarMode.value).toBe('hidden')
    })
  })

  describe('toggle behavior', () => {
    it('should toggle sidebar visibility on mobile', () => {
      setViewportWidth(500)
      const { isVisible, toggle } = useSidebar()
      expect(isVisible.value).toBe(false)

      toggle()
      expect(isVisible.value).toBe(true)

      toggle()
      expect(isVisible.value).toBe(false)
    })

    it('should toggle sidebar expansion on tablet', () => {
      setViewportWidth(800)
      const { isExpanded, toggle } = useSidebar()
      expect(isExpanded.value).toBe(false)

      toggle()
      expect(isExpanded.value).toBe(true)

      toggle()
      expect(isExpanded.value).toBe(false)
    })

    it('should close sidebar explicitly', () => {
      setViewportWidth(500)
      const { isVisible, toggle, close } = useSidebar()

      toggle() // Open
      expect(isVisible.value).toBe(true)

      close()
      expect(isVisible.value).toBe(false)
    })

    it('should open sidebar explicitly', () => {
      setViewportWidth(500)
      const { isVisible, open } = useSidebar()
      expect(isVisible.value).toBe(false)

      open()
      expect(isVisible.value).toBe(true)
    })
  })

  describe('responsive transitions', () => {
    it('should update state when viewport changes from desktop to tablet', () => {
      setViewportWidth(1024)
      let sidebar = useSidebar()
      expect(sidebar.sidebarMode.value).toBe('expanded')

      setViewportWidth(800)
      sidebar = useSidebar()
      expect(sidebar.sidebarMode.value).toBe('collapsed')
      expect(sidebar.isExpanded.value).toBe(false)
    })

    it('should update state when viewport changes from tablet to mobile', () => {
      setViewportWidth(800)
      let sidebar = useSidebar()
      expect(sidebar.isVisible.value).toBe(true)

      setViewportWidth(500)
      sidebar = useSidebar()
      expect(sidebar.sidebarMode.value).toBe('hidden')
      expect(sidebar.isVisible.value).toBe(false)
    })

    it('should update state when viewport changes from mobile to desktop', () => {
      setViewportWidth(500)
      let sidebar = useSidebar()
      expect(sidebar.isVisible.value).toBe(false)

      setViewportWidth(1024)
      sidebar = useSidebar()
      expect(sidebar.sidebarMode.value).toBe('expanded')
      expect(sidebar.isVisible.value).toBe(true)
    })
  })

  describe('breakpoint boundaries', () => {
    it('should treat 1024px as desktop', () => {
      setViewportWidth(1024)
      const { sidebarMode } = useSidebar()
      expect(sidebarMode.value).toBe('expanded')
    })

    it('should treat 1023px as tablet', () => {
      setViewportWidth(1023)
      const { sidebarMode } = useSidebar()
      expect(sidebarMode.value).toBe('collapsed')
    })

    it('should treat 768px as tablet', () => {
      setViewportWidth(768)
      const { sidebarMode } = useSidebar()
      expect(sidebarMode.value).toBe('collapsed')
    })

    it('should treat 767px as mobile', () => {
      setViewportWidth(767)
      const { sidebarMode } = useSidebar()
      expect(sidebarMode.value).toBe('hidden')
    })
  })
})
