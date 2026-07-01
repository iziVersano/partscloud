<script setup>
import { ref, onErrorCaptured } from "vue";

const error = ref(null);

onErrorCaptured((err) => {
  error.value = err;
  return false;
});
</script>

<template>
  <div v-if="error" class="error-boundary">
    <h2>Something went wrong</h2>
    <p>{{ error.message }}</p>
    <button @click="error = null">Try again</button>
  </div>
  <slot v-else />
</template>

<style scoped>
.error-boundary {
  max-width: 480px;
  margin: 6rem auto;
  text-align: center;
  padding: 2rem;
  background: white;
  border: 1px solid #fecaca;
  border-radius: 10px;
}
.error-boundary h2 {
  font-size: 1.2rem;
  color: #991b1b;
  margin: 0 0 0.5rem;
}
.error-boundary p {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0 0 1.5rem;
}
.error-boundary button {
  padding: 0.45rem 1.2rem;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: white;
  cursor: pointer;
  font-size: 0.85rem;
}
.error-boundary button:hover {
  background: #f3f4f6;
}
</style>
