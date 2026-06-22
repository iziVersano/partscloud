<script setup>
import { useInventoryStore } from "../store/inventoryStore";

const store = useInventoryStore();

const filters = [
  { label: "All", value: null },
  { label: "Critical", value: "critical" },
  { label: "Warning", value: "warning" },
  { label: "OK", value: "ok" },
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
        :class="{ active: store.riskFilter === f.value }"
        @click="select(f.value)"
      >
        {{ f.label }}
      </button>
    </div>

    <template v-if="store.selectedCount > 0">
      <div class="divider" />
      <span class="selected-count">{{ store.selectedCount }} selected</span>
      <button class="bulk-btn accept" @click="store.bulkAct('accepted')">Accept all</button>
      <button class="bulk-btn decline" @click="store.bulkAct('declined')">Decline all</button>
      <button class="clear-btn" @click="store.clearSelection()">Clear</button>
    </template>

    <span class="count">{{ store.visibleSkus.length }} shown</span>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 0.6rem;
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
  padding: 0.4rem 1rem;
  border-radius: 999px;
  border: none;
  background: transparent;
  font-size: 0.85rem;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
}
.filter-btn:hover {
  color: #111827;
}
.filter-btn.active {
  background: white;
  color: #111827;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}
.divider {
  width: 1px;
  height: 1.2rem;
  background: #d1d5db;
  margin: 0 0.2rem;
}
.selected-count {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e3a8a;
  white-space: nowrap;
}
.bulk-btn {
  padding: 0.35rem 0.85rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  white-space: nowrap;
}
.bulk-btn.accept {
  background: #16a34a;
  color: white;
}
.bulk-btn.accept:hover {
  background: #15803d;
}
.bulk-btn.decline {
  background: white;
  border-color: #d1d5db;
  color: #374151;
}
.bulk-btn.decline:hover {
  background: #f3f4f6;
}
.clear-btn {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 0.82rem;
  cursor: pointer;
  text-decoration: underline;
  white-space: nowrap;
}
.count {
  margin-left: auto;
  color: #6b7280;
  font-size: 0.85rem;
  white-space: nowrap;
}
</style>
