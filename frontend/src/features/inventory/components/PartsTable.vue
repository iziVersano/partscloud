<script setup>
import { computed } from "vue";
import { useInventoryStore } from "../store/inventoryStore";
import PartRow from "./PartRow.vue";

const store = useInventoryStore();

const columns = [
  { label: "SKU", field: "sku" },
  { label: "Name", field: "name" },
  { label: "Category", field: "category" },
  { label: "On hand", field: "on_hand" },
  { label: "Risk", field: "risk_score" },
  { label: "Status", field: "action_status" },
];

function sortBy(field) {
  store.setSort(field);
}

// Select-all operates on the current page, not every filtered row across
// all pages — selection itself is still tracked globally (a Set of SKU
// ids), so checking boxes on page 1, then page 2, accumulates correctly.
const allOnPageSelected = computed(() =>
  store.paginatedSkus.length > 0 &&
  store.paginatedSkus.every((row) => store.selected.has(row.sku))
);

function toggleSelectAll() {
  if (allOnPageSelected.value) {
    store.paginatedSkus.forEach((row) => store.selected.delete(row.sku));
  } else {
    store.paginatedSkus.forEach((row) => store.selected.add(row.sku));
  }
}
</script>

<template>
  <div class="table-card">
    <table class="parts-table">
      <thead>
        <tr>
          <th class="checkbox-col">
            <input
              type="checkbox"
              :checked="allOnPageSelected"
              @change="toggleSelectAll"
            />
          </th>
          <th
            v-for="col in columns"
            :key="col.field"
            @click="sortBy(col.field)"
            class="sortable"
          >
            {{ col.label }}
            <span v-if="store.sortField === col.field" class="sort-arrow">
              {{ store.sortDir === "asc" ? "▲" : "▼" }}
            </span>
          </th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <PartRow
          v-for="row in store.paginatedSkus"
          :key="row.sku"
          :row="row"
        />
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.table-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}
.parts-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
}
.parts-table th {
  padding: 0.7rem 0.9rem;
  text-align: left;
  vertical-align: middle;
}
.parts-table thead th {
  background: #f9fafb;
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: #6b7280;
  border-bottom: 1px solid #e5e7eb;
}
.parts-table th.sortable {
  cursor: pointer;
  user-select: none;
}
.parts-table th.sortable:hover {
  color: #374151;
}
.sort-arrow {
  font-size: 0.7rem;
}
.checkbox-col {
  width: 2.5rem;
}
.parts-table input[type="checkbox"] {
  accent-color: #2563eb;
  width: 16px;
  height: 16px;
  cursor: pointer;
}
</style>
