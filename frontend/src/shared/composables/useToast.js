import { ref, readonly } from "vue";

// Module-level singleton queue so any component can raise a toast without
// prop-drilling or a store dependency.
const toasts = ref([]);
let nextId = 0;

function push(message, tone = "ok", timeout = 3000) {
  const id = ++nextId;
  toasts.value.push({ id, message, tone });
  if (timeout > 0) {
    setTimeout(() => dismiss(id), timeout);
  }
  return id;
}

function dismiss(id) {
  const i = toasts.value.findIndex((t) => t.id === id);
  if (i !== -1) toasts.value.splice(i, 1);
}

export function useToast() {
  return {
    toasts: readonly(toasts),
    dismiss,
    success: (msg, timeout) => push(msg, "ok", timeout),
    error: (msg, timeout) => push(msg, "critical", timeout),
    info: (msg, timeout) => push(msg, "accent", timeout),
  };
}
