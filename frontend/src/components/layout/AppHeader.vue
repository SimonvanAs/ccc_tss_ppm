<script setup lang="ts">
withDefaults(
  defineProps<{
    showHamburger?: boolean
  }>(),
  {
    showHamburger: false,
  }
)

const emit = defineEmits<{
  (e: 'toggle-sidebar'): void
}>()

function toggleSidebar() {
  emit('toggle-sidebar')
}
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <button
        v-if="showHamburger"
        class="hamburger-btn"
        type="button"
        aria-label="Toggle sidebar"
        @click="toggleSidebar"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z" />
        </svg>
      </button>
      <span class="brand-text">TSS PPM</span>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  height: 60px;
  background-color: var(--color-white);
  border-bottom: 1px solid var(--color-gray-200);
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.hamburger-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-navy);
}

.hamburger-btn:hover {
  background-color: var(--color-gray-100);
}

.brand-text {
  font-size: 1.125rem;
  font-weight: bold;
  color: var(--color-navy);
}
</style>
