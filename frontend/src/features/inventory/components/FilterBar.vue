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
    <button
      v-for="f in filters"
      :key="f.label"
      :class="{ active: store.riskFilter === f.value }"
      @click="select(f.value)"
    >
      {{ f.label }}
    </button>

    <span class="count">{{ store.visibleSkus.length }} shown</span>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 1rem;
}
.filter-bar button.active {
  font-weight: 700;
  text-decoration: underline;
}
.count {
  margin-left: auto;
  color: #666;
  font-size: 0.9rem;
}
</style>
