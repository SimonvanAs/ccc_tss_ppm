// TSS PPM v3.0 - Vue Application Entry Point
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createI18n } from 'vue-i18n'
import App from './App.vue'

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
      path: '/reviews/:reviewId/goals',
      name: 'GoalSetting',
      component: () => import('./views/GoalSettingView.vue'),
      props: true,
    },
  ]
})

// Create and mount app
const app = createApp(App)
app.use(i18n)
app.use(router)
app.mount('#app')
