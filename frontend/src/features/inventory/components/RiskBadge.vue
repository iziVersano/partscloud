<script setup>
import BasePill from "../../../shared/ui/BasePill.vue";

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
  <BasePill :tone="risk" dot>{{ labels[risk] || risk }}</BasePill>
</template>
