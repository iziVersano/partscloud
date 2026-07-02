<script setup>
import { computed } from "vue";

const props = defineProps({
  status: {
    type: String,
    required: true,
  },
  // Optional: when a critical SKU is still pending, escalate the label to
  // "Action needed" instead of a plain "Pending" — nobody has triaged a
  // stockout risk yet. Purely derived, no separate stored state.
  risk: {
    type: String,
    default: null,
  },
});

const labels = {
  pending: "Pending",
  accepted: "Accepted",
  declined: "Declined",
};

const isUrgent = computed(() => props.status === "pending" && props.risk === "critical");
const displayKey = computed(() => (isUrgent.value ? "urgent" : props.status));
</script>

<template>
  <span class="status" :class="displayKey">
    <svg
      v-if="status === 'accepted'"
      width="14"
      height="14"
      viewBox="0 0 16 16"
      aria-hidden="true"
    >
      <path
        d="M3 8.5l3 3 7-7"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
    <svg
      v-else-if="status === 'declined'"
      width="14"
      height="14"
      viewBox="0 0 16 16"
      aria-hidden="true"
    >
      <path
        d="M4 4l8 8M12 4l-8 8"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
      />
    </svg>
    <svg v-else-if="isUrgent" width="14" height="14" viewBox="0 0 16 16" aria-hidden="true">
      <path
        d="M8 2l7 12H1L8 2z"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linejoin="round"
      />
      <path d="M8 6.5v3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
      <circle cx="8" cy="11.5" r="0.9" fill="currentColor" />
    </svg>
    <svg v-else width="14" height="14" viewBox="0 0 16 16" aria-hidden="true">
      <circle
        cx="8"
        cy="8"
        r="6.5"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
      />
      <path
        d="M8 4.5v3.5l2.5 1.5"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
      />
    </svg>
    {{ isUrgent ? "Action needed" : labels[status] || status }}
  </span>
</template>

<style scoped>
.status {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.85rem;
  font-weight: 500;
}
.status.pending {
  color: var(--c-muted);
}
.status.accepted {
  color: var(--c-ok);
}
.status.declined {
  color: var(--c-critical);
}
.status.urgent {
  color: var(--c-critical);
  font-weight: 700;
}
</style>
