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
    <span>{{ store.selectedCount }} selected</span>
    <button @click="acceptSelected">Accept all</button>
    <button @click="declineSelected">Decline all</button>
    <button @click="store.clearSelection()" class="clear">Clear</button>
  </div>
</template>

<style scoped>
.bulk-bar {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  padding: 0.6rem 1rem;
  background: #f3f4f6;
  border-radius: 6px;
  margin-bottom: 1rem;
}
.bulk-bar .clear {
  margin-left: auto;
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
}
</style>
