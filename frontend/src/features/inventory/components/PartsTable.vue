<script setup>
import { computed } from "vue";
import { useInventoryStore } from "../store/inventoryStore";
import RiskBadge from "./RiskBadge.vue";
import StatusIcon from "./StatusIcon.vue";

const store = useInventoryStore();

const columns = [
  { label: "SKU", field: "sku" },
  { label: "Name", field: "name" },
  { label: "Category", field: "category" },
  { label: "On hand", field: "on_hand" },
  { label: "Risk", field: "risk_score" },
  { label: "Status", field: "action_status" },
];

function onCheckboxChange(sku) {
  store.toggleSelected(sku);
}

function accept(sku) {
  store.act(sku, "accepted");
}

function decline(sku) {
  store.act(sku, "declined");
}

function sortBy(field) {
  store.setSort(field);
}

// Select-all operates on the current page, not every filtered row across
// all pages — selection itself is still tracked globally (a Set of SKU
// ids), so checking boxes on page 1, then page 2, accumulates correctly.
const allOnPageSelected = computed(() =>
  store.paginatedSkus.length > 0 &&
  store.paginatedSkus.every((row) => store.isSelected(row.sku))
);

function toggleSelectAll() {
  if (allOnPageSelected.value) {
    store.paginatedSkus.forEach((row) => {
      const i = store.selected.indexOf(row.sku);
      if (i !== -1) store.selected.splice(i, 1);
    });
  } else {
    store.paginatedSkus.forEach((row) => {
      if (!store.isSelected(row.sku)) store.selected.push(row.sku);
    });
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
        <tr v-for="row in store.paginatedSkus" :key="row.sku">
          <td class="checkbox-col">
            <input
              type="checkbox"
              :checked="store.isSelected(row.sku)"
              @change="onCheckboxChange(row.sku)"
            />
          </td>
          <td class="mono">{{ row.sku }}</td>
          <td>{{ row.name }}</td>
          <td class="muted">{{ row.category }}</td>
          <td class="mono">{{ row.on_hand }}</td>
          <td><RiskBadge :risk="row.risk" /></td>
          <td><StatusIcon :status="row.action_status" /></td>
          <td class="actions">
            <button
              class="btn accept"
              @click="accept(row.sku)"
              :disabled="row.action_status === 'accepted'"
            >
              Accept
            </button>
            <button
              class="btn decline"
              @click="decline(row.sku)"
              :disabled="row.action_status === 'declined'"
            >
              Decline
            </button>
          </td>
        </tr>
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
.parts-table th,
.parts-table td {
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
.parts-table tbody tr {
  border-bottom: 1px solid #f1f2f4;
}
.parts-table tbody tr:last-child {
  border-bottom: none;
}
.parts-table tbody tr:hover {
  background: #fafbfc;
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
.mono {
  font-family: "SF Mono", "Roboto Mono", Consolas, monospace;
  font-size: 0.88rem;
  color: #374151;
}
.muted {
  color: #6b7280;
}
.actions {
  white-space: nowrap;
}
.btn {
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  margin-right: 0.4rem;
}
.btn.accept {
  background: #f0fdf4;
  border-color: #bbf7d0;
  color: #166534;
}
.btn.accept:hover:not(:disabled) {
  background: #dcfce7;
}
.btn.decline {
  background: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}
.btn.decline:hover:not(:disabled) {
  background: #fee2e2;
}
.btn:disabled {
  opacity: 0.4;
  cursor: default;
}
</style>
