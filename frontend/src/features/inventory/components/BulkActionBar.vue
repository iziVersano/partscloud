<script setup>
import { useInventoryStore } from "../store/inventoryStore";

const store = useInventoryStore();

function acceptSelected() {
  store.bulkAct("accepted");
}

function declineSelected() {
  store.bulkAct("declined");
}
</script>

<template>
  <div v-if="store.selectedCount > 0" class="bulk-bar">
    <span class="count">{{ store.selectedCount }} selected</span>
    <button class="btn accept" @click="acceptSelected">Accept all</button>
    <button class="btn decline" @click="declineSelected">Decline all</button>
    <button class="clear" @click="store.clearSelection()">Clear</button>
  </div>
</template>

<style scoped>
.bulk-bar {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  padding: 0.7rem 1rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  margin-bottom: 1rem;
}
.count {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e3a8a;
}
.btn {
  padding: 0.35rem 0.85rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
}
.btn.accept {
  background: #16a34a;
  color: white;
}
.btn.accept:hover {
  background: #15803d;
}
.btn.decline {
  background: white;
  border-color: #d1d5db;
  color: #374151;
}
.btn.decline:hover {
  background: #f3f4f6;
}
.clear {
  margin-left: auto;
  background: none;
  border: none;
  color: #6b7280;
  font-size: 0.82rem;
  cursor: pointer;
  text-decoration: underline;
}
</style>
