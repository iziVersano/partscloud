<script setup>
import { useInventoryStore } from "../store/inventoryStore";
import SearchBar from "./SearchBar.vue";

const store = useInventoryStore();

const filters = [
  { label: "All", value: null, key: "all" },
  { label: "Critical", value: "critical", key: "critical" },
  { label: "Warning", value: "warning", key: "warning" },
  { label: "OK", value: "ok", key: "ok" },
];

function select(value) {
  store.setRiskFilter(value);
}
</script>

<template>
  <div class="filter-bar">
    <div class="filter-group">
      <button
        v-for="f in filters"
        :key="f.label"
        class="filter-btn"
        :class="[f.key, { active: store.riskFilter === f.value }]"
        :aria-pressed="store.riskFilter === f.value"
        @click="select(f.value)"
      >
        <svg
          v-if="f.key !== 'all'"
          class="dot"
          width="7"
          height="7"
          viewBox="0 0 8 8"
          aria-hidden="true"
        >
          <circle cx="4" cy="4" r="4" />
        </svg>
        {{ f.label }}
      </button>
    </div>

    <div v-if="store.selectedCount > 0" class="bulk-inline" role="region" aria-label="Bulk actions">
      <span class="bulk-count" aria-live="polite">
        {{ store.bulkPending ? "Working…" : `${store.selectedCount} selected` }}
      </span>
      <button class="bulk-btn accept" @click="store.bulkAct('accepted')" :disabled="store.bulkPending">Accept selected</button>
      <button class="bulk-btn decline" @click="store.bulkAct('declined')" :disabled="store.bulkPending">Decline selected</button>
      <button class="bulk-clear" @click="store.clearSelection()" :disabled="store.bulkPending">Clear</button>
    </div>

    <SearchBar class="search-slot" />

    <span class="count">{{ store.skus.length }} of {{ store.total }}</span>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--sp-2);
  margin-bottom: var(--sp-4);
}
.filter-group {
  display: flex;
  gap: 0.4rem;
  background: var(--c-surface-2);
  padding: 0.25rem;
  border-radius: var(--r-pill);
}
.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 1rem;
  border-radius: var(--r-pill);
  border: none;
  background: transparent;
  font-size: var(--fs-sm);
  font-weight: 500;
  color: var(--c-ink-soft);
  cursor: pointer;
  transition: background var(--dur) var(--ease), color var(--dur) var(--ease);
}
.filter-btn .dot circle {
  fill: currentColor;
}
.filter-btn:hover {
  color: var(--c-ink);
}
.filter-btn:focus-visible {
  outline: 2px solid var(--c-purple);
  outline-offset: 2px;
}
.filter-btn.active {
  box-shadow: var(--shadow-sm);
}

/* All: neutral */
.filter-btn.all.active {
  background: var(--c-surface);
  color: var(--c-ink);
}

/* Critical: red */
.filter-btn.critical {
  color: var(--c-critical);
}
.filter-btn.critical.active {
  background: var(--c-critical-bg);
  color: var(--c-critical);
}

/* Warning: amber */
.filter-btn.warning {
  color: var(--c-warning);
}
.filter-btn.warning.active {
  background: var(--c-warning-bg);
  color: var(--c-warning);
}

/* OK: green */
.filter-btn.ok {
  color: var(--c-ok);
}
.filter-btn.ok.active {
  background: var(--c-ok-bg);
  color: var(--c-ok);
}

.bulk-inline {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  margin-left: var(--sp-4);
  padding-left: var(--sp-4);
  border-left: 2px solid var(--c-line);
}
.bulk-count {
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--c-purple-strong);
}
.bulk-btn {
  padding: 0.3rem 0.75rem;
  border-radius: var(--r-sm);
  font-size: var(--fs-sm);
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
}
.bulk-btn.accept {
  background: var(--c-green);
  color: white;
}
.bulk-btn.accept:hover { filter: brightness(0.93); }
.bulk-btn.decline {
  background: var(--c-critical-bg);
  border-color: transparent;
  color: var(--c-critical);
}
.bulk-btn.decline:hover { filter: brightness(0.97); }
.bulk-clear {
  background: none;
  border: none;
  color: var(--c-muted);
  font-size: var(--fs-sm);
  cursor: pointer;
  text-decoration: underline;
}
.bulk-btn:disabled,
.bulk-clear:disabled {
  opacity: 0.5;
  cursor: default;
}
.bulk-btn:focus-visible,
.bulk-clear:focus-visible {
  outline: 2px solid var(--c-purple);
  outline-offset: 2px;
}
.search-slot {
  margin-left: auto;
}
.count {
  color: var(--c-muted);
  font-size: var(--fs-sm);
  white-space: nowrap;
}

@media (max-width: 720px) {
  .filter-bar {
    align-items: stretch;
  }
  /* Filter pills scroll horizontally instead of wrapping into stacked rows. */
  .filter-group {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  /* Search takes its own full-width row below the pills. */
  .search-slot {
    margin-left: 0;
    order: 3;
    flex-basis: 100%;
  }
  .count {
    order: 2;
    margin-left: auto;
    align-self: center;
  }
  .bulk-inline {
    order: 4;
    flex-basis: 100%;
    margin-left: 0;
    padding-left: 0;
    border-left: none;
    flex-wrap: wrap;
  }
}
</style>
