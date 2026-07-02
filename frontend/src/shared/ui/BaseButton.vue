<script setup>
defineProps({
  variant: {
    type: String,
    default: "default",
    validator: (v) => ["default", "primary", "ghost", "danger", "pill"].includes(v),
  },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  block: { type: Boolean, default: false },
});

defineEmits(["click"]);
</script>

<template>
  <button
    class="btn"
    :class="[`btn--${variant}`, { 'btn--block': block }]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="btn__spinner" aria-hidden="true" />
    <slot />
  </button>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--sp-2);
  padding: 0.4rem 0.9rem;
  border-radius: var(--r-sm);
  border: 1px solid transparent;
  font-size: var(--fs-sm);
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: background var(--dur) var(--ease), border-color var(--dur) var(--ease),
    opacity var(--dur) var(--ease);
}
.btn--block {
  width: 100%;
}
.btn:disabled {
  opacity: 0.55;
  cursor: default;
}
.btn:focus-visible {
  outline: 2px solid var(--c-purple);
  outline-offset: 2px;
}

.btn--default {
  background: var(--c-surface);
  border-color: var(--c-line);
  color: var(--c-ink-soft);
}
.btn--default:hover:not(:disabled) {
  background: var(--c-surface-2);
}

.btn--primary {
  background: var(--c-purple);
  color: #fff;
}
.btn--primary:hover:not(:disabled) {
  background: var(--c-purple-strong);
}

.btn--pill {
  background: var(--c-pill);
  color: var(--c-pill-ink);
  border-radius: var(--r-pill);
}
.btn--pill:hover:not(:disabled) {
  opacity: 0.9;
}

.btn--ghost {
  background: transparent;
  color: var(--c-muted);
}
.btn--ghost:hover:not(:disabled) {
  background: var(--c-surface-2);
  color: var(--c-ink);
}

.btn--danger {
  background: var(--c-critical-bg);
  border-color: transparent;
  color: var(--c-critical);
}
.btn--danger:hover:not(:disabled) {
  filter: brightness(0.97);
}

.btn__spinner {
  width: 12px;
  height: 12px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: btn-spin 0.6s linear infinite;
}
@keyframes btn-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
