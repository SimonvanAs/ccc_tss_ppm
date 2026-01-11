<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { getCurrentUser } from './api/auth'

const { t, locale } = useI18n()
const user = getCurrentUser()

const isManager = computed(() => {
  return user?.roles?.includes('manager') ?? false
})

function changeLocale(lang: string) {
  locale.value = lang
  localStorage.setItem('locale', lang)
}
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="header-left">
        <RouterLink to="/" class="brand">
          <h1>{{ t('app.title') }}</h1>
        </RouterLink>
        <nav class="main-nav">
          <RouterLink to="/" class="nav-link">{{ t('nav.dashboard') }}</RouterLink>
          <RouterLink v-if="isManager" to="/team" class="nav-link">{{ t('nav.team') }}</RouterLink>
        </nav>
      </div>
      <div class="header-right">
        <div class="language-switcher">
          <button @click="changeLocale('en')" :class="{ active: locale === 'en' }">EN</button>
          <button @click="changeLocale('nl')" :class="{ active: locale === 'nl' }">NL</button>
          <button @click="changeLocale('es')" :class="{ active: locale === 'es' }">ES</button>
        </div>
      </div>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style>
:root {
  --color-magenta: #CC0E70;
  --color-navy: #004A91;
  --color-white: #FFFFFF;
  --color-gray-100: #F5F5F5;
  --color-gray-200: #E0E0E0;
  --color-gray-600: #666666;
  --color-gray-900: #1A1A1A;

  /* 9-Grid colors */
  --color-grid-red: #DC2626;
  --color-grid-orange: #F59E0B;
  --color-grid-green: #22C55E;
  --color-grid-dark-green: #15803D;

  /* Additional grays */
  --color-gray-300: #D1D5DB;
  --color-gray-500: #6B7280;
  --color-gray-700: #374151;

  /* Error color */
  --color-error: #DC2626;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Tahoma, Verdana, Segoe, sans-serif;
  background-color: var(--color-gray-100);
  color: var(--color-gray-900);
}

/* Base form input styles */
input,
select,
textarea {
  font-family: Tahoma, Verdana, Segoe, sans-serif;
  font-size: 0.875rem;
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--color-gray-300);
  border-radius: 6px;
  background-color: var(--color-white);
  color: var(--color-gray-900);
  width: 100%;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: var(--color-magenta);
  box-shadow: 0 0 0 3px rgba(204, 14, 112, 0.1);
}

input::placeholder,
textarea::placeholder {
  color: var(--color-gray-500);
}

input:disabled,
select:disabled,
textarea:disabled {
  background-color: var(--color-gray-100);
  cursor: not-allowed;
  opacity: 0.7;
}

select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236B7280' d='M6 8L2 4h8z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  padding-right: 2.5rem;
}

textarea {
  resize: vertical;
  min-height: 80px;
}

/* Voice input padding adjustment */
input[data-voice-enabled="true"],
textarea[data-voice-enabled="true"] {
  padding-right: 2.5rem;
}

.app {
  min-height: 100vh;
}

.header {
  background-color: var(--color-navy);
  color: var(--color-white);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.brand {
  text-decoration: none;
  color: var(--color-white);
}

.brand h1 {
  margin: 0;
  font-size: 1.25rem;
}

.main-nav {
  display: flex;
  gap: 1rem;
}

.nav-link {
  color: var(--color-white);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
  background-color: var(--color-magenta);
}

.header-right {
  display: flex;
  align-items: center;
}

.language-switcher button {
  background: transparent;
  border: 1px solid var(--color-white);
  color: var(--color-white);
  padding: 0.25rem 0.5rem;
  margin-left: 0.25rem;
  cursor: pointer;
  font-family: inherit;
}

.language-switcher button.active {
  background: var(--color-magenta);
  border-color: var(--color-magenta);
}

.language-switcher button:hover {
  background: var(--color-magenta);
  border-color: var(--color-magenta);
}

main {
  padding: 1rem;
}
</style>
