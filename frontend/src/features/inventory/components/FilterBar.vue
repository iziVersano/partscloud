<script setup>
import { useInventoryStore } from "../store/inventoryStore";

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

    <span class="count">{{ store.skus.length }} of {{ store.total }}</span>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.filter-group {
  display: flex;
  gap: 0.4rem;
  background: #f3f4f6;
  padding: 0.25rem;
  border-radius: 999px;
}
.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 1rem;
  border-radius: 999px;
  border: none;
  background: transparent;
  font-size: 0.85rem;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
}
.filter-btn .dot circle {
  fill: currentColor;
}
.filter-btn:hover {
  color: #111827;
}
.filter-btn:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}
.filter-btn.active {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

/* All: neutral */
.filter-btn.all.active {
  background: white;
  color: #111827;
}

/* Critical: red */
.filter-btn.critical {
  color: #b91c1c;
}
.filter-btn.critical.active {
  background: #fee2e2;
  color: #991b1b;
}

/* Warning: amber */
.filter-btn.warning {
  color: #b45309;
}
.filter-btn.warning.active {
  background: #fef3c7;
  color: #92400e;
}

/* OK: green */
.filter-btn.ok {
  color: #15803d;
}
.filter-btn.ok.active {
  background: #dcfce7;
  color: #166534;
}

.bulk-inline {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: 1rem;
  padding-left: 1rem;
  border-left: 2px solid #d1d5db;
}
.bulk-count {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e3a8a;
}
.bulk-btn {
  padding: 0.3rem 0.75rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
}
.bulk-btn.accept {
  background: #16a34a;
  color: white;
}
.bulk-btn.accept:hover { background: #15803d; }
.bulk-btn.decline {
  background: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}
.bulk-btn.decline:hover { background: #fee2e2; }
.bulk-clear {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 0.82rem;
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
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}
.count {
  margin-left: auto;
  color: #6b7280;
  font-size: 0.85rem;
}
</style>
