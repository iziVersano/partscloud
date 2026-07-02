<script setup>
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
      <svg v-if="theme === 'dark'" width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="5" fill="none" stroke="currentColor" stroke-width="2" />
        <g stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M12 1v3M12 20v3M23 12h-3M4 12H1M20.5 3.5l-2 2M5.5 18.5l-2 2M20.5 20.5l-2-2M5.5 5.5l-2-2" />
        </g>
      </svg>
      <svg v-else width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M21 12.5A9 9 0 1 1 11.5 3a7 7 0 0 0 9.5 9.5z"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linejoin="round"
        />
      </svg>
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
