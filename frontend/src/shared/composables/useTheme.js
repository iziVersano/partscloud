import { ref, watch, readonly } from "vue";

const STORAGE_KEY = "partscloud-theme";

function initialTheme() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

// Module-level singleton: the theme is app-wide, so all callers share one
// reactive source rather than each creating an independent copy.
const theme = ref(initialTheme());

watch(
  theme,
  (value) => {
    document.documentElement.setAttribute("data-theme", value);
    localStorage.setItem(STORAGE_KEY, value);
  },
  { immediate: true }
);

export function useTheme() {
  function toggle() {
    theme.value = theme.value === "dark" ? "light" : "dark";
  }
  return { theme: readonly(theme), toggle };
}
