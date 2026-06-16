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
  <span class="badge" :class="risk">
    <svg class="dot" width="8" height="8" viewBox="0 0 8 8" aria-hidden="true">
      <circle cx="4" cy="4" r="4" />
    </svg>
    {{ labels[risk] || risk }}
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  line-height: 1;
}
.badge .dot {
  flex-shrink: 0;
}
.badge.critical {
  background-color: #fee2e2;
  color: #991b1b;
}
.badge.critical .dot circle {
  fill: #dc2626;
}
.badge.warning {
  background-color: #fef3c7;
  color: #92400e;
}
.badge.warning .dot circle {
  fill: #d97706;
}
.badge.ok {
  background-color: #dcfce7;
  color: #166534;
}
.badge.ok .dot circle {
  fill: #16a34a;
}
</style>
