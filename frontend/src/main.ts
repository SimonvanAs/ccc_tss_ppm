// TSS PPM v3.0 - Vue Application Entry Point
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import { initAuth } from './api/auth'
import { initAnalytics } from './composables/useAnalytics'

// Import translations
import en from './i18n/en.json'
import nl from './i18n/nl.json'
import es from './i18n/es.json'

// i18n configuration
const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'en',
  fallbackLocale: 'en',
  messages: { en, nl, es }
})

// Router configuration
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: () => import('./views/DashboardView.vue'),
    },
    {
      path: '/team',
      name: 'TeamDashboard',
      component: () => import('./views/TeamDashboardView.vue'),
    },
    {
      path: '/reviews/:reviewId/goals',
      name: 'GoalSetting',
      component: () => import('./views/GoalSettingView.vue'),
      props: true,
    },
    {
      path: '/reviews/:reviewId/score',
      name: 'ReviewScoring',
      component: () => import('./views/ReviewScoringView.vue'),
      props: true,
    },
    {
      path: '/calibration',
      name: 'Calibration',
      component: () => import('./views/CalibrationView.vue'),
    },
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('./views/AdminView.vue'),
    },
  ]
})

// Initialize authentication, then mount app
initAuth().then((authenticated) => {
  if (authenticated) {
    // Initialize analytics (Plausible)
    initAnalytics()

    const app = createApp(App)
    app.use(i18n)
    app.use(router)
    app.mount('#app')
  } else {
    console.error('Authentication failed')
  }
})
