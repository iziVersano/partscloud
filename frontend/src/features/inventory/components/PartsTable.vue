<script setup>
import { computed, ref } from "vue";
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

function ariaSortFor(field) {
  if (store.sortField !== field) return "none";
  return store.sortDir === "asc" ? "ascending" : "descending";
}

// Select-all operates on the current page, not every filtered row across
// all pages — selection itself is still tracked globally, so checking
// boxes on page 1, then page 2, accumulates correctly.
const allOnPageSelected = computed(() =>
  store.skus.length > 0 &&
  store.skus.every((row) => store.selected.includes(row.sku))
);

function toggleSelectAll() {
  store.toggleSelectAll();
}

const dropdownOpen = ref(false);

function selectAll() {
  store.skus.forEach((row) => {
    if (!store.selected.includes(row.sku)) store.toggleSelected(row.sku);
  });
  dropdownOpen.value = false;
}

function selectNone() {
  store.clearSelection();
  dropdownOpen.value = false;
}
</script>

<template>
  <div class="table-card">
    <table class="parts-table">
      <caption class="visually-hidden">
        Spare parts inventory, sorted by {{ columns.find(c => c.field === store.sortField)?.label }}
      </caption>
      <thead>
        <tr>
          <th scope="col" class="checkbox-col">
            <div class="select-all-wrap">
              <input
                type="checkbox"
                :checked="allOnPageSelected"
                @change="toggleSelectAll"
                aria-label="Select all rows on this page"
              />
              <button
                class="chevron-btn"
                @click="dropdownOpen = !dropdownOpen"
                aria-label="Selection options"
              >▾</button>
              <div v-if="dropdownOpen" class="select-dropdown">
                <button @click="selectAll">All</button>
                <button @click="selectNone">None</button>
              </div>
            </div>
          </th>
          <th
            v-for="col in columns"
            :key="col.field"
            scope="col"
            class="sortable"
            tabindex="0"
            :aria-sort="ariaSortFor(col.field)"
            @click="sortBy(col.field)"
            @keydown.enter="sortBy(col.field)"
            @keydown.space.prevent="sortBy(col.field)"
          >
            {{ col.label }}
            <span v-if="store.sortField === col.field" class="sort-arrow" aria-hidden="true">
              {{ store.sortDir === "asc" ? "▲" : "▼" }}
            </span>
          </th>
          <th scope="col">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in store.skus" :key="row.sku">
          <td class="checkbox-col" data-label="Select">
            <input
              type="checkbox"
              :checked="store.selected.includes(row.sku)"
              @change="onCheckboxChange(row.sku)"
              :aria-label="`Select ${row.sku}`"
            />
          </td>
          <td class="mono" data-label="SKU">{{ row.sku }}</td>
          <td data-label="Name">{{ row.name }}</td>
          <td class="muted" data-label="Category">{{ row.category }}</td>
          <td class="mono" data-label="On hand">{{ row.on_hand }}</td>
          <td data-label="Risk"><RiskBadge :risk="row.risk" /></td>
          <td data-label="Status"><StatusIcon :status="row.action_status" /></td>
          <td class="actions" data-label="Action">
            <button
              class="btn accept"
              @click="accept(row.sku)"
              :disabled="row.action_status === 'accepted' || store.isPending(row.sku) || store.bulkPending"
            >
              <span v-if="store.isPending(row.sku)" class="spinner" aria-hidden="true"></span>
              {{ store.isPending(row.sku) ? "Saving…" : "Accept" }}
            </button>
            <button
              class="btn decline"
              @click="decline(row.sku)"
              :disabled="row.action_status === 'declined' || store.isPending(row.sku) || store.bulkPending"
            >
              <span v-if="store.isPending(row.sku)" class="spinner" aria-hidden="true"></span>
              {{ store.isPending(row.sku) ? "Saving…" : "Decline" }}
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
.parts-table th.sortable:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: -2px;
}
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
.sort-arrow {
  font-size: 0.7rem;
}
.checkbox-col {
  width: 4rem;
}
.select-all-wrap {
  position: relative;
  display: flex;
  align-items: center;
  gap: 2px;
}
.chevron-btn {
  background: none;
  border: none;
  padding: 0 2px;
  cursor: pointer;
  font-size: 0.75rem;
  color: #6b7280;
  line-height: 1;
}
.chevron-btn:hover {
  color: #111827;
}
.select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 10;
  min-width: 80px;
  overflow: hidden;
}
.select-dropdown button {
  display: block;
  width: 100%;
  padding: 0.45rem 0.85rem;
  background: none;
  border: none;
  text-align: left;
  font-size: 0.85rem;
  cursor: pointer;
  color: #111827;
}
.select-dropdown button:hover {
  background: #f3f4f6;
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
  min-width: 4.5rem;
  white-space: nowrap;
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
  opacity: 0.6;
  cursor: default;
}
.spinner {
  display: inline-block;
  width: 10px;
  height: 10px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  vertical-align: middle;
  margin-right: 4px;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .parts-table thead {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
  }
  .parts-table,
  .parts-table tbody,
  .parts-table tr {
    display: block;
    width: 100%;
  }
  .parts-table tbody tr {
    padding: 0.75rem 0.9rem;
  }
  .parts-table td {
    display: block;
    width: 100%;
    box-sizing: border-box;
    padding: 0.3rem 0;
    text-align: left;
  }
  .parts-table td[data-label]::before {
    content: attr(data-label);
    display: block;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: #6b7280;
  }
  .parts-table td.checkbox-col {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .parts-table td.checkbox-col::before {
    content: attr(data-label);
    font-size: 0.85rem;
    font-weight: 500;
    color: #374151;
    text-transform: none;
    letter-spacing: normal;
  }
}
</style>
