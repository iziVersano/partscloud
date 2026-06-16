# shared/composables

Reserved for reusable Vue composition functions shared across features
(e.g. `useDebounce`, `usePagination`, `usePolling`).

Empty for now — `inventoryStore.js` covers this feature's state needs
on its own. This becomes useful the moment two features need the same
piece of reusable logic (e.g. if a future "suppliers" feature also
needs debounced search).
