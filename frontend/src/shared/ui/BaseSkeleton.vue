<script setup>
defineProps({
  width: { type: String, default: "100%" },
  height: { type: String, default: "1rem" },
  radius: { type: String, default: "var(--r-sm)" },
});
</script>

<template>
  <span
    class="skeleton"
    :style="{ width, height, borderRadius: radius }"
    aria-hidden="true"
  />
</template>

<style scoped>
.skeleton {
  display: block;
  background: linear-gradient(
    90deg,
    var(--c-surface-2) 25%,
    var(--c-line) 37%,
    var(--c-surface-2) 63%
  );
  background-size: 400% 100%;
  animation: shimmer 1.3s ease infinite;
}
@keyframes shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}
@media (prefers-reduced-motion: reduce) {
  .skeleton {
    animation: none;
  }
}
</style>
