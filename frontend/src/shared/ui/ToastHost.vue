<script setup>
import { useToast } from "../composables/useToast";

const { toasts, dismiss } = useToast();
</script>

<template>
  <Teleport to="body">
    <div class="toast-host" role="status" aria-live="polite">
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="toast"
          :class="`toast--${t.tone}`"
          @click="dismiss(t.id)"
        >
          {{ t.message }}
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-host {
  position: fixed;
  bottom: var(--sp-5);
  right: var(--sp-5);
  z-index: 60;
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
  pointer-events: none;
}
.toast {
  pointer-events: auto;
  min-width: 240px;
  max-width: 340px;
  padding: 0.7rem 1rem;
  border-radius: var(--r-md);
  font-size: var(--fs-sm);
  font-weight: 500;
  color: #fff;
  box-shadow: var(--shadow-md);
  cursor: pointer;
}
.toast--ok {
  background: var(--c-green);
}
.toast--critical {
  background: var(--c-red);
}
.toast--accent {
  background: var(--c-purple);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity var(--dur) var(--ease), transform var(--dur) var(--ease);
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
