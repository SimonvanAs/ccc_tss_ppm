<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import { useSidebar } from '../../composables/useSidebar'

const { t } = useI18n()
const {
  sidebarMode,
  isVisible,
  showHamburger,
  toggle,
  close,
} = useSidebar()

function scrollToMain() {
  document.getElementById('main-content')?.focus()
}
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
    <!-- Skip to main content link -->
    <a
      href="#main-content"
      class="skip-link"
      @click.prevent="scrollToMain"
    >
      {{ t('layout.header.skipToMain') }}
    </a>

    <!-- Mobile overlay -->
    <div
      v-if="sidebarMode === 'hidden' && isVisible"
      class="sidebar-overlay"
      aria-hidden="true"
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
      <main
        id="main-content"
        class="app-content"
        tabindex="-1"
        :aria-label="t('layout.mainContent.ariaLabel')"
      >
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
/* Skip to main content link - visible only on focus */
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
  z-index: 100;
  padding: 0.75rem 1rem;
  background-color: var(--color-navy);
  color: var(--color-white);
  text-decoration: none;
  font-weight: 500;
  border-radius: 0 0 4px 0;
  transition: top 0.2s ease;
}

.skip-link:focus {
  top: 0;
  outline: 2px solid var(--color-magenta);
  outline-offset: 2px;
}

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
