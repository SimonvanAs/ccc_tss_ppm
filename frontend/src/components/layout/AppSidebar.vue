<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getCurrentUser } from '../../api/auth'

const { t } = useI18n()
const route = useRoute()
const user = getCurrentUser()

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

function isActive(path: string): boolean {
  return route.path === path
}
</script>

<template>
  <aside class="app-sidebar">
    <div class="sidebar-brand">
      <span class="brand-text">TSS PPM</span>
    </div>

    <nav class="sidebar-nav">
      <RouterLink
        to="/"
        class="nav-item"
        :class="{ 'is-active': isActive('/') }"
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
  background-color: var(--color-navy);
  color: var(--color-white);
  display: flex;
  flex-direction: column;
}

.sidebar-brand {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.brand-text {
  font-size: 1.25rem;
  font-weight: bold;
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
  color: var(--color-white);
  text-decoration: none;
  transition: background-color 0.2s;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-item.is-active {
  background-color: var(--color-magenta);
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.nav-label {
  font-size: 0.9375rem;
}

.sidebar-profile {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
