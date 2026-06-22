<script setup>
import { useInventoryStore } from "../store/inventoryStore";
import RiskBadge from "./RiskBadge.vue";
import StatusIcon from "./StatusIcon.vue";

defineProps({
  row: { type: Object, required: true },
});

const store = useInventoryStore();
</script>

<template>
  <tr>
    <td class="checkbox-col">
      <input
        type="checkbox"
        :checked="store.selected.has(row.sku)"
        @change="store.toggleSelected(row.sku)"
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
        @click="store.act(row.sku, 'accepted')"
        :disabled="row.action_status === 'accepted'"
      >
        Accept
      </button>
      <button
        class="btn decline"
        @click="store.act(row.sku, 'declined')"
        :disabled="row.action_status === 'declined'"
      >
        Decline
      </button>
    </td>
  </tr>
</template>

<style scoped>
tr {
  border-bottom: 1px solid #f1f2f4;
}
tr:last-child {
  border-bottom: none;
}
tr:hover {
  background: #fafbfc;
}
td {
  padding: 0.7rem 0.9rem;
  text-align: left;
  vertical-align: middle;
  font-size: 0.92rem;
}
.checkbox-col {
  width: 2.5rem;
}
input[type="checkbox"] {
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
