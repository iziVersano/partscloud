<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from "vue";

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: "" },
});
const emit = defineEmits(["close"]);

const panel = ref(null);

function onKeydown(e) {
  if (e.key === "Escape") {
    emit("close");
    return;
  }
  // Minimal focus trap: keep Tab focus inside the panel while open.
  if (e.key === "Tab" && panel.value) {
    const focusable = panel.value.querySelectorAll(
      'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
}

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
      document.addEventListener("keydown", onKeydown);
      await nextTick();
      panel.value?.focus();
    } else {
      document.body.style.overflow = "";
      document.removeEventListener("keydown", onKeydown);
    }
  }
);

onBeforeUnmount(() => {
  document.body.style.overflow = "";
  document.removeEventListener("keydown", onKeydown);
});
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="open" class="drawer-root">
        <div class="drawer-backdrop" @click="emit('close')" />
        <div
          ref="panel"
          class="drawer-panel"
          role="dialog"
          aria-modal="true"
          :aria-label="title"
          tabindex="-1"
        >
          <header class="drawer-header">
            <h2 class="drawer-title">{{ title }}</h2>
            <button class="drawer-close" aria-label="Close" @click="emit('close')">×</button>
          </header>
          <div class="drawer-body">
            <slot />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.drawer-root {
  position: fixed;
  inset: 0;
  z-index: 50;
}
.drawer-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
}
.drawer-panel {
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  width: min(480px, 100%);
  background: var(--c-surface);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  outline: none;
}
.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--sp-4) var(--sp-5);
  border-bottom: 1px solid var(--c-line);
}
.drawer-title {
  margin: 0;
  font-size: var(--fs-lg);
  font-weight: 700;
  color: var(--c-ink);
}
.drawer-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: var(--c-muted);
  cursor: pointer;
}
.drawer-close:hover {
  color: var(--c-ink);
}
.drawer-body {
  padding: var(--sp-5);
  overflow-y: auto;
  flex: 1;
}

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity var(--dur) var(--ease);
}
.drawer-enter-active .drawer-panel,
.drawer-leave-active .drawer-panel {
  transition: transform var(--dur) var(--ease);
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
.drawer-enter-from .drawer-panel,
.drawer-leave-to .drawer-panel {
  transform: translateX(100%);
}
</style>
