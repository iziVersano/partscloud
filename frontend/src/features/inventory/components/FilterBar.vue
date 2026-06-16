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

    <span class="count">{{ store.visibleSkus.length }} shown</span>
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
.count {
  margin-left: auto;
  color: #6b7280;
  font-size: 0.85rem;
}
</style>
