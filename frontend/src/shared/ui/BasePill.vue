<script setup>
// Small status pill. `tone` maps to a semantic color; `dot` shows a leading dot.
defineProps({
  tone: {
    type: String,
    default: "neutral",
    validator: (v) => ["neutral", "critical", "warning", "ok", "accent"].includes(v),
  },
  dot: { type: Boolean, default: false },
});
</script>

<template>
  <span class="pill" :class="`pill--${tone}`">
    <span v-if="dot" class="pill__dot" aria-hidden="true" />
    <slot />
  </span>
</template>

<style scoped>
.pill {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  padding: 0.22rem 0.6rem;
  border-radius: var(--r-pill);
  font-size: var(--fs-sm);
  font-weight: 600;
  line-height: 1.1;
  white-space: nowrap;
}
.pill__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
}
.pill--neutral {
  background: var(--c-surface-2);
  color: var(--c-muted);
}
.pill--critical {
  background: var(--c-critical-bg);
  color: var(--c-critical);
}
.pill--warning {
  background: var(--c-warning-bg);
  color: var(--c-warning);
}
.pill--ok {
  background: var(--c-ok-bg);
  color: var(--c-ok);
}
.pill--accent {
  background: var(--c-purple-bg);
  color: var(--c-purple-strong);
}
</style>
