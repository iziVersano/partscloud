<script setup>
import { Sun, Moon } from "@lucide/vue";
import { useTheme } from "../composables/useTheme";

const { theme, toggle } = useTheme();
</script>

<template>
  <header class="topbar">
    <div class="topbar__brand">
      <svg class="topbar__mark" width="26" height="26" viewBox="0 0 26 26" aria-hidden="true">
        <path d="M2 15 C2 8, 8 2, 15 2" fill="none" stroke="var(--c-purple)" stroke-width="3.5" stroke-linecap="round" />
        <circle cx="19" cy="6" r="3.5" fill="var(--c-purple)" />
        <circle cx="6" cy="19" r="3" fill="var(--c-green)" />
      </svg>
      <div>
        <h1 class="topbar__title">PartsCloud</h1>
        <p class="topbar__subtitle">Stockout risk for spare-part inventory</p>
      </div>
    </div>

    <button
      class="topbar__theme-toggle"
      type="button"
      @click="toggle"
      :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
    >
      <Sun v-if="theme === 'dark'" :size="18" aria-hidden="true" />
      <Moon v-else :size="18" aria-hidden="true" />
    </button>
  </header>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--sp-6);
}
.topbar__brand {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
}
.topbar__mark {
  flex-shrink: 0;
}
.topbar__title {
  font-size: var(--fs-xl);
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.01em;
  color: var(--c-ink);
}
.topbar__subtitle {
  margin: 0;
  color: var(--c-muted);
  font-size: var(--fs-md);
}
.topbar__theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--r-pill);
  border: 1px solid var(--c-line);
  background: var(--c-surface);
  color: var(--c-ink-soft);
  cursor: pointer;
  transition: background var(--dur) var(--ease), color var(--dur) var(--ease);
}
.topbar__theme-toggle:hover {
  background: var(--c-surface-2);
  color: var(--c-ink);
}
.topbar__theme-toggle:focus-visible {
  outline: 2px solid var(--c-purple);
  outline-offset: 2px;
}
</style>
