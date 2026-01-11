<script setup lang="ts">
import { ref } from 'vue'

const showCredits = ref(false)

const credits = [
  'Graciela van der Stroom',
  'Tjerk Venrooy',
  'Simon van As',
]

function toggleCredits() {
  showCredits.value = !showCredits.value
}
</script>

<template>
  <footer class="app-footer">
    <!-- View Source -->
    <a
      href="https://github.com/SimonvanAs/ccc_tss_ppm"
      target="_blank"
      rel="noopener noreferrer"
      class="footer-section footer-link"
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
      </svg>
      <span>View Source</span>
    </a>

    <!-- Built with AI -->
    <div class="footer-section ai-section">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"/>
        <circle cx="7.5" cy="14.5" r="1.5"/>
        <circle cx="16.5" cy="14.5" r="1.5"/>
      </svg>
      <span>Built with the help of AI</span>
    </div>

    <!-- Developer Credits -->
    <div class="footer-section credits-section">
      <button
        class="credits-btn"
        type="button"
        :aria-expanded="showCredits"
        @click="toggleCredits"
      >
        <span>Developer Credits</span>
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="chevron"
          :class="{ 'chevron-up': showCredits }"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>
      <div v-if="showCredits" class="credits-dropdown">
        <div v-for="name in credits" :key="name" class="credit-item">
          {{ name }}
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 0.75rem 1.5rem;
  background-color: var(--color-white);
  border-top: 1px solid var(--color-gray-200);
  font-size: 0.875rem;
  color: var(--color-gray-600);
}

.footer-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* View Source Link */
.footer-link {
  color: var(--color-gray-600);
  text-decoration: none;
  transition: color 0.2s;
}

.footer-link:hover {
  color: var(--color-navy);
}

/* AI Section */
.ai-section {
  flex: 1;
  justify-content: center;
  color: var(--color-gray-500);
}

/* Credits Section */
.credits-section {
  position: relative;
}

.credits-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-gray-600);
  font-size: 0.875rem;
  transition: all 0.2s;
}

.credits-btn:hover {
  background-color: var(--color-gray-100);
  color: var(--color-navy);
}

.chevron {
  transition: transform 0.2s;
}

.chevron-up {
  transform: rotate(180deg);
}

.credits-dropdown {
  position: absolute;
  bottom: 100%;
  right: 0;
  margin-bottom: 0.5rem;
  padding: 0.5rem 0;
  background-color: var(--color-white);
  border: 1px solid var(--color-gray-200);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 180px;
}

.credit-item {
  padding: 0.5rem 1rem;
  color: var(--color-gray-700);
  white-space: nowrap;
}

/* Responsive */
@media (max-width: 768px) {
  .app-footer {
    flex-wrap: wrap;
    gap: 1rem;
    padding: 1rem;
  }

  .ai-section {
    flex: none;
  }

  .ai-section span {
    display: none;
  }
}
</style>
