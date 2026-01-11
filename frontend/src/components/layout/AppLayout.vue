<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import { useSidebar } from '../../composables/useSidebar'

const {
  sidebarMode,
  isVisible,
  showHamburger,
  toggle,
  close,
} = useSidebar()
</script>

<template>
  <div
    class="app-layout"
    :class="{
      'app-layout--sidebar-expanded': sidebarMode === 'expanded',
      'app-layout--sidebar-collapsed': sidebarMode === 'collapsed',
      'app-layout--sidebar-hidden': sidebarMode === 'hidden',
    }"
  >
    <!-- Mobile overlay -->
    <div
      v-if="sidebarMode === 'hidden' && isVisible"
      class="sidebar-overlay"
      @click="close"
    />

    <AppSidebar
      :mode="sidebarMode"
      :is-open="isVisible"
      @close="close"
    />
    <div class="app-main">
      <AppHeader
        :show-hamburger="showHamburger"
        @toggle-sidebar="toggle"
      />
      <div class="app-content">
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: grid;
  grid-template-columns: auto 1fr;
  min-height: 100vh;
  position: relative;
}

.app-layout--sidebar-hidden {
  grid-template-columns: 1fr;
}

.app-main {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  overflow: hidden;
}

.app-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background-color: var(--color-gray-100);
}

/* Mobile overlay */
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 40;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Responsive adjustments */
@media (max-width: 767px) {
  .app-content {
    padding: 1rem;
  }
}
</style>
