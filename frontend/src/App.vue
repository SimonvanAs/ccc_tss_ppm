<script setup lang="ts">
import { AppLayout } from './components/layout'
</script>

<template>
  <AppLayout>
    <router-view />
  </AppLayout>
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
</style>
