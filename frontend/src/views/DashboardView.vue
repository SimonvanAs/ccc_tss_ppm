<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { getCurrentUser, logout } from '../api/auth'
import { RouterLink } from 'vue-router'

const { t } = useI18n()
const user = getCurrentUser()
</script>

<template>
  <div class="dashboard">
    <h2>{{ t('dashboard.title') }}</h2>
    <p>{{ t('dashboard.welcome') }}</p>

    <div class="user-info" v-if="user">
      <h3>Logged in as:</h3>
      <p><strong>Email:</strong> {{ user.email }}</p>
      <p><strong>Name:</strong> {{ user.name }}</p>
      <p><strong>Roles:</strong> {{ user.roles.join(', ') }}</p>
      <button @click="logout" class="logout-btn">Logout</button>
    </div>

    <div class="quick-links">
      <h3>Quick Links</h3>
      <RouterLink to="/reviews/33333333-3333-3333-3333-333333333333/goals" class="link-btn">
        Go to Goal Setting (Demo)
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

h2 {
  color: var(--color-navy);
  margin-bottom: 1rem;
}

h3 {
  color: var(--color-navy);
  margin-top: 2rem;
  margin-bottom: 0.5rem;
}

.user-info {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.user-info p {
  margin: 0.5rem 0;
}

.logout-btn {
  margin-top: 1rem;
  background: var(--color-magenta);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-family: inherit;
}

.logout-btn:hover {
  opacity: 0.9;
}

.quick-links {
  margin-top: 2rem;
}

.link-btn {
  display: inline-block;
  background: var(--color-navy);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  margin-top: 0.5rem;
}

.link-btn:hover {
  opacity: 0.9;
}
</style>
