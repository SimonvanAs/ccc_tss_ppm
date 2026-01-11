// TSS PPM v3.0 - Sidebar State Management Composable
import { ref, computed, watch } from 'vue'

type SidebarMode = 'expanded' | 'collapsed' | 'hidden'

const BREAKPOINTS = {
  desktop: 1024,
  tablet: 768,
}

// Shared reactive state (singleton pattern for cross-component sharing)
const viewportWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)
const manuallyToggled = ref(false)
const manualState = ref(false)

// Set up global resize listener once
let resizeListenerAttached = false

function attachResizeListener() {
  if (typeof window === 'undefined' || resizeListenerAttached) return

  const updateViewportWidth = () => {
    const newWidth = window.innerWidth
    if (newWidth !== viewportWidth.value) {
      viewportWidth.value = newWidth
      // Reset manual toggle when viewport changes
      manuallyToggled.value = false
    }
  }

  window.addEventListener('resize', updateViewportWidth)
  resizeListenerAttached = true
}

function getDefaultMode(width: number): SidebarMode {
  if (width >= BREAKPOINTS.desktop) return 'expanded'
  if (width >= BREAKPOINTS.tablet) return 'collapsed'
  return 'hidden'
}

export function useSidebar() {
  // Attach listener on first use
  attachResizeListener()

  const defaultMode = computed(() => getDefaultMode(viewportWidth.value))

  const sidebarMode = computed<SidebarMode>(() => {
    if (!manuallyToggled.value) {
      return defaultMode.value
    }

    // On mobile: manual toggle controls visibility
    if (defaultMode.value === 'hidden') {
      return manualState.value ? 'expanded' : 'hidden'
    }

    // On tablet: manual toggle controls expansion
    if (defaultMode.value === 'collapsed') {
      return manualState.value ? 'expanded' : 'collapsed'
    }

    // On desktop: always expanded
    return 'expanded'
  })

  const isExpanded = computed(() => sidebarMode.value === 'expanded')
  const isCollapsed = computed(() => sidebarMode.value === 'collapsed')
  const isHidden = computed(() => sidebarMode.value === 'hidden')
  const isVisible = computed(() => sidebarMode.value !== 'hidden')

  const showHamburger = computed(() => {
    return viewportWidth.value < BREAKPOINTS.desktop
  })

  function toggle() {
    manuallyToggled.value = true
    manualState.value = !manualState.value
  }

  function close() {
    manuallyToggled.value = true
    manualState.value = false
  }

  function open() {
    manuallyToggled.value = true
    manualState.value = true
  }

  return {
    // State
    sidebarMode,
    isExpanded,
    isCollapsed,
    isHidden,
    isVisible,
    showHamburger,
    viewportWidth,

    // Actions
    toggle,
    close,
    open,
  }
}

// Export for testing - allows resetting state between tests
export function _resetSidebarState() {
  viewportWidth.value = typeof window !== 'undefined' ? window.innerWidth : 1024
  manuallyToggled.value = false
  manualState.value = false
}
