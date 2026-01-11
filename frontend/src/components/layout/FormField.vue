<script setup lang="ts">
defineProps<{
  label: string
  id?: string
  required?: boolean
  voiceEnabled?: boolean
  error?: string
}>()

const emit = defineEmits<{
  (e: 'voice-click'): void
}>()

function handleVoiceClick() {
  emit('voice-click')
}
</script>

<template>
  <div class="form-field" :class="{ 'form-field--error': error }">
    <label :for="id" class="form-field__label">
      {{ label }}
      <span v-if="required" class="form-field__required">*</span>
    </label>
    <div class="form-field__input">
      <slot />
      <button
        v-if="voiceEnabled"
        type="button"
        class="form-field__voice"
        aria-label="Voice input"
        @click="handleVoiceClick"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path
            d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"
          />
        </svg>
      </button>
    </div>
    <p v-if="error" class="form-field__error">{{ error }}</p>
  </div>
</template>

<style scoped>
.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-field__label {
  font-family: Tahoma, sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray-700);
}

.form-field__required {
  color: var(--color-magenta);
  margin-left: 0.125rem;
}

.form-field__input {
  position: relative;
  display: flex;
  align-items: center;
}

.form-field__input :slotted(input),
.form-field__input :slotted(select),
.form-field__input :slotted(textarea) {
  flex: 1;
}

.form-field__voice {
  position: absolute;
  right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-gray-500);
  transition: color 0.2s, background-color 0.2s;
}

.form-field__voice:hover {
  color: var(--color-magenta);
  background-color: var(--color-gray-100);
}

.form-field__error {
  font-size: 0.75rem;
  color: var(--color-error, #dc2626);
  margin: 0;
}

.form-field--error .form-field__label {
  color: var(--color-error, #dc2626);
}
</style>
