<script setup>
import { useInventoryStore } from "../store/inventoryStore";
import RiskBadge from "./RiskBadge.vue";

const store = useInventoryStore();

function onCheckboxChange(sku) {
  store.toggleSelected(sku);
}

function accept(sku) {
  store.act(sku, "accepted");
}

function decline(sku) {
  store.act(sku, "declined");
}
</script>

<template>
  <table class="parts-table">
    <thead>
      <tr>
        <th></th>
        <th>SKU</th>
        <th>Name</th>
        <th>Category</th>
        <th>On hand</th>
        <th>Risk</th>
        <th>Status</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="row in store.visibleSkus" :key="row.sku">
        <td>
          <input
            type="checkbox"
            :checked="store.selected.has(row.sku)"
            @change="onCheckboxChange(row.sku)"
          />
        </td>
        <td>{{ row.sku }}</td>
        <td>{{ row.name }}</td>
        <td>{{ row.category }}</td>
        <td>{{ row.on_hand }}</td>
        <td><RiskBadge :risk="row.risk" /></td>
        <td>{{ row.action_status }}</td>
        <td>
          <button @click="accept(row.sku)" :disabled="row.action_status === 'accepted'">
            Accept
          </button>
          <button @click="decline(row.sku)" :disabled="row.action_status === 'declined'">
            Decline
          </button>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.parts-table {
  width: 100%;
  border-collapse: collapse;
}
.parts-table th,
.parts-table td {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #e5e5e5;
  text-align: left;
}
.parts-table button {
  margin-right: 0.4rem;
}
</style>
