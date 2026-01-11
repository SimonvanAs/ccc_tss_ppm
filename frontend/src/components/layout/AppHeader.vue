<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const props = withDefaults(
  defineProps<{
    progress?: number
    showHamburger?: boolean
  }>(),
  {
    progress: 0,
    showHamburger: false,
  }
)

const emit = defineEmits<{
  (e: 'locale-change', locale: string): void
  (e: 'toggle-sidebar'): void
}>()

const { locale } = useI18n()

const languages = [
  { code: 'en', label: 'EN' },
  { code: 'nl', label: 'NL' },
  { code: 'es', label: 'ES' },
]

function changeLocale(code: string) {
  locale.value = code
  try {
    localStorage.setItem('locale', code)
  } catch {
    // localStorage not available in some environments
  }
  emit('locale-change', code)
}

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

    <div class="header-center">
      <div class="progress-wrapper">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progress}%` }" />
        </div>
        <span class="progress-label">{{ progress }}% Complete</span>
      </div>
    </div>

    <div class="header-right">
      <div class="language-selector">
        <button
          v-for="lang in languages"
          :key="lang.code"
          class="lang-btn"
          :class="{ 'is-active': locale === lang.code }"
          type="button"
          @click="changeLocale(lang.code)"
        >
          {{ lang.label }}
        </button>
      </div>
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
  justify-content: space-between;
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

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-bar {
  width: 200px;
  height: 8px;
  background-color: var(--color-gray-200);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--color-magenta);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-label {
  font-size: 0.875rem;
  color: var(--color-gray-600);
  white-space: nowrap;
}

.header-right {
  display: flex;
  align-items: center;
}

.language-selector {
  display: flex;
  gap: 0.25rem;
}

.lang-btn {
  padding: 0.375rem 0.75rem;
  background: transparent;
  border: 1px solid var(--color-gray-200);
  border-radius: 4px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-gray-600);
  transition: all 0.2s;
}

.lang-btn:hover {
  background-color: var(--color-gray-100);
  border-color: var(--color-gray-300);
}

.lang-btn.is-active {
  background-color: var(--color-magenta);
  border-color: var(--color-magenta);
  color: var(--color-white);
}
</style>
