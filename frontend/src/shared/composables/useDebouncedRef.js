import { ref, watch, readonly } from "vue";

// Returns an immediate ref (bind this to v-model) plus a debounced readonly ref
// that only updates `delay` ms after writes stop. Watch the debounced one to
// trigger expensive work (e.g. a search request) without firing per keystroke.
export function useDebouncedRef(initial = "", delay = 300) {
  const immediate = ref(initial);
  const debounced = ref(initial);
  let timeout;

  watch(immediate, (value) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      debounced.value = value;
    }, delay);
  });

  return { immediate, debounced: readonly(debounced) };
}
