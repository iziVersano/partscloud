<script setup>
defineProps({
  risk: {
    type: String,
    required: true,
  },
});

const labels = {
  critical: "Critical",
  warning: "Warning",
  ok: "OK",
};
</script>

<template>
  <span class="badge" :class="risk">{{ labels[risk] || risk }}</span>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  color: white;
}
.badge.critical {
  background-color: #d92d20;
}
.badge.warning {
  background-color: #d4a017;
}
.badge.ok {
  background-color: #1a7f37;
}
</style>
