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

    <span class="count">{{ store.total }} shown</span>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
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

.count {
  margin-left: auto;
  color: #6b7280;
  font-size: 0.85rem;
}
</style>
