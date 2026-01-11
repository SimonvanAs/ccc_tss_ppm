<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getCurrentUser } from '../../api/auth'

type SidebarMode = 'expanded' | 'collapsed' | 'hidden'

const props = withDefaults(
  defineProps<{
    mode?: SidebarMode
    isOpen?: boolean
  }>(),
  {
    mode: 'expanded',
    isOpen: true,
  }
)

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'locale-change', locale: string): void
}>()

const { t, locale } = useI18n()
const route = useRoute()
const user = getCurrentUser()

// Language options
const languages = [
  { code: 'en', label: 'English' },
  { code: 'nl', label: 'Nederlands' },
  { code: 'es', label: 'Español' },
]

const isManager = computed(() => {
  return user?.roles?.includes('manager') ?? false
})

const userInitials = computed(() => {
  if (!user?.name) return '?'
  const parts = user.name.split(' ')
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
  }
  return user.name[0]?.toUpperCase() || '?'
})

const isCollapsed = computed(() => props.mode === 'collapsed')
const isMobileOpen = computed(() => props.mode === 'hidden' && props.isOpen)

function isActive(path: string): boolean {
  return route.path === path
}

function handleNavClick() {
  // Close sidebar on mobile after navigation
  if (props.mode === 'hidden') {
    emit('close')
  }
}

function changeLocale(code: string) {
  locale.value = code
  try {
    localStorage.setItem('locale', code)
  } catch {
    // localStorage not available in some environments
  }
  emit('locale-change', code)
}
</script>

<template>
  <aside
    class="app-sidebar"
    :class="{
      'app-sidebar--collapsed': isCollapsed,
      'app-sidebar--hidden': mode === 'hidden' && !isOpen,
      'app-sidebar--mobile-open': isMobileOpen,
    }"
  >
    <div class="sidebar-header">
      <div class="sidebar-brand">
        <span class="brand-text">TSS PPM</span>
      </div>

      <div class="language-selector">
        <button
          v-for="lang in languages"
          :key="lang.code"
          class="lang-btn"
          :class="{ 'is-active': locale === lang.code }"
          type="button"
          :title="lang.label"
          @click="changeLocale(lang.code)"
        >
          <!-- UK Flag -->
          <svg v-if="lang.code === 'en'" width="20" height="14" viewBox="0 0 60 42" class="flag-icon">
            <rect width="60" height="42" fill="#012169"/>
            <path d="M0,0 L60,42 M60,0 L0,42" stroke="#fff" stroke-width="6"/>
            <path d="M0,0 L60,42 M60,0 L0,42" stroke="#C8102E" stroke-width="4" stroke-dasharray="1,1,1,42" stroke-dashoffset="1"/>
            <path d="M30,0 V42 M0,21 H60" stroke="#fff" stroke-width="10"/>
            <path d="M30,0 V42 M0,21 H60" stroke="#C8102E" stroke-width="6"/>
          </svg>
          <!-- Netherlands Flag -->
          <svg v-else-if="lang.code === 'nl'" width="20" height="14" viewBox="0 0 60 42" class="flag-icon">
            <rect width="60" height="14" fill="#AE1C28"/>
            <rect y="14" width="60" height="14" fill="#FFF"/>
            <rect y="28" width="60" height="14" fill="#21468B"/>
          </svg>
          <!-- Spain Flag -->
          <svg v-else-if="lang.code === 'es'" width="20" height="14" viewBox="0 0 60 42" class="flag-icon">
            <rect width="60" height="42" fill="#AA151B"/>
            <rect y="10.5" width="60" height="21" fill="#F1BF00"/>
          </svg>
        </button>
      </div>
    </div>

    <nav class="sidebar-nav">
      <RouterLink
        to="/"
        class="nav-item"
        :class="{ 'is-active': isActive('/') }"
        @click="handleNavClick"
      >
        <span class="nav-icon">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
          </svg>
        </span>
        <span class="nav-label">{{ t('nav.dashboard') }}</span>
      </RouterLink>

      <RouterLink
        v-if="isManager"
        to="/team"
        class="nav-item"
        :class="{ 'is-active': isActive('/team') }"
        @click="handleNavClick"
      >
        <span class="nav-icon">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
          </svg>
        </span>
        <span class="nav-label">{{ t('nav.team') }}</span>
      </RouterLink>
    </nav>

    <div class="sidebar-profile">
      <div class="profile-avatar">
        <img
          v-if="user?.picture"
          :src="user.picture"
          :alt="user?.name || 'User avatar'"
          class="avatar-image"
        />
        <span v-else class="avatar-initials">{{ userInitials }}</span>
      </div>
      <div class="profile-info">
        <span class="profile-name">{{ user?.name || 'User' }}</span>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.app-sidebar {
  width: 240px;
  min-height: 100vh;
  background-color: var(--color-white);
  color: var(--color-navy);
  border-right: 1px solid var(--color-gray-200);
  display: flex;
  flex-direction: column;
  transition: width 0.25s ease, transform 0.25s ease;
  z-index: 50;
}

/* Collapsed state (tablet) */
.app-sidebar--collapsed {
  width: 64px;
}

.app-sidebar--collapsed .brand-text,
.app-sidebar--collapsed .nav-label,
.app-sidebar--collapsed .profile-info,
.app-sidebar--collapsed .lang-label,
.app-sidebar--collapsed .language-selector {
  display: none;
}

.app-sidebar--collapsed .sidebar-header {
  padding: 1rem 0.75rem;
}

.app-sidebar--collapsed .sidebar-brand {
  justify-content: center;
}

.app-sidebar--collapsed .nav-item {
  justify-content: center;
  padding: 0.75rem;
}

.app-sidebar--collapsed .sidebar-profile {
  justify-content: center;
  padding: 1rem 0.75rem;
}

/* Hidden state (mobile - default hidden) */
.app-sidebar--hidden {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  transform: translateX(-100%);
}

/* Mobile open state (slide in from left) */
.app-sidebar--mobile-open {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  transform: translateX(0);
  width: 280px;
  box-shadow: 4px 0 16px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-gray-200);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.brand-text {
  font-size: 1.25rem;
  font-weight: bold;
  color: var(--color-magenta);
}

.language-selector {
  display: flex;
  gap: 0.5rem;
}

.lang-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.375rem;
  background: transparent;
  border: 2px solid transparent;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  opacity: 0.6;
}

.lang-btn:hover {
  opacity: 1;
  background-color: var(--color-gray-100);
}

.lang-btn.is-active {
  opacity: 1;
  border-color: var(--color-magenta);
  background-color: rgba(204, 14, 112, 0.08);
}

.flag-icon {
  display: block;
  border-radius: 2px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  color: var(--color-navy);
  text-decoration: none;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background-color: var(--color-gray-100);
}

.nav-item.is-active {
  background-color: rgba(204, 14, 112, 0.1);
  border-left-color: var(--color-magenta);
  color: var(--color-magenta);
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.nav-label {
  font-size: 0.9375rem;
  white-space: nowrap;
}

.sidebar-profile {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-gray-200);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.profile-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--color-magenta);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-initials {
  font-size: 0.875rem;
  font-weight: bold;
  color: var(--color-white);
}

.profile-info {
  flex: 1;
  min-width: 0;
}

.profile-name {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-navy);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
