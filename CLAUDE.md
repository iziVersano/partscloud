# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Run everything
```bash
docker compose up          # backend :8000, frontend :5173, runs tests then exits
```

### Backend (from repo root)
```bash
# Run all tests
docker compose run --rm tests

# Run tests locally (faster, no Docker)
cd backend
python manage.py test apps.inventory --settings=partscloud.settings.test

# Run a single test module
python manage.py test apps.inventory.tests.test_risk --settings=partscloud.settings.test

# Apply migrations / re-seed
python manage.py migrate --settings=partscloud.settings.dev

# Start dev server locally
python manage.py runserver --settings=partscloud.settings.dev
```

### Frontend (from repo root)
```bash
cd frontend
npm install
npm run dev       # Vite dev server with proxy to backend on /api
npm run build
```

## Architecture

### Backend: Django + DRF

Layered pattern: **repositories → services → API views**

- `apps/inventory/repositories/sku_repository.py` — all DB access; no ORM queries outside here
- `apps/inventory/services/risk.py` — pure risk computation (no DB); `compute_risk_fields()` is the main entry point
- `apps/inventory/services/actions.py` — accept/decline logic for single and bulk operations
- `apps/inventory/api/v1/views.py` — 3 endpoints: `GET /api/v1/skus`, `POST /api/v1/skus/<sku_id>/action`, `POST /api/v1/skus/actions`

**Risk model** (`services/risk.py`):
```
projected = on_hand - (avg_daily_demand × lead_time_days)
CRITICAL if projected < 0
WARNING  if projected < safety_stock
OK       otherwise
risk_score = projected - safety_stock  (negative = at risk, used for sorting)
```
Zero demand → OK (avoids divide-by-zero in days-of-cover logic). Risk is computed once at seed time and stored on the `SKU` row — not recalculated per request.

**Seed data** is loaded via migration `0002_seed_inventory.py` (idempotent). The risk formula is inlined there deliberately to avoid migration fragility if the service signature changes — see that file's docstring.

**Settings** live in `partscloud/settings/`: `base.py` (shared), `dev.py` (file SQLite, debug), `test.py` (in-memory SQLite). Always pass `--settings=partscloud.settings.test` when running tests.

### Frontend: Vue 3 + Pinia + Vite

Feature-based layout under `src/features/inventory/`:

- `api/inventoryApi.js` — fetch wrappers; base URL `/api/v1`; Vite proxies `/api` → `localhost:8000`
- `store/inventoryStore.js` — single Pinia store; owns all state (skus, filters, sort, pagination, selection, loading/error); filtering/sorting/pagination are **client-side getters** (`visibleSkus` → `paginatedSkus`)
- Components: `PartsTable`, `FilterBar`, `BulkActionBar`, `Pagination`, `RiskBadge`, `StatusIcon`; `App.vue` is the composition root

**Selection uses a plain array** (not `Set`) because Vue 3 does not track `Set` mutations reactively.

### Key model fields (`SKU`)

`sku`, `name`, `category`, `on_hand`, `avg_daily_demand`, `lead_time_days`, `safety_stock`, `unit_cost_eur`, `last_delivery_date`, `risk` (critical/warning/ok), `risk_score` (float), `action_status` (pending/accepted/declined)

## Open work in flight (not yet on main)

These exist as open PRs/branches and are not part of `main` yet — don't assume their behavior when reading code on `main`:

- **Configurable per-category risk policy** (`feat/configurable-risk-policy`, PR #11) — adds `RiskPolicy` / `CATEGORY_POLICIES` to `services/risk_policy.py`, lets `compute_risk()` take a policy override per category (Bearings ×2.0, Drives ×1.5, Chains ×1.5 warning multiplier). Seed migration applies the same multipliers so it reaches served data, not just direct calls to `compute_risk()`.
- **Hardened CSV ingestion** (`feat/harden-csv-import`, PR #12) — adds `services/importer.py` to validate rows (required fields, numeric/date parsing, rejects negative values), a new `import_skus` management command, and the same validation inlined into the seed migration. Bad rows are skipped and logged, not silently admitted or fatal.
- **Server-side pagination/filtering/sorting** (`feat/server-side-pagination`, PR #13) — moves filtering/sorting/pagination from frontend getters (`visibleSkus`/`paginatedSkus`) to query params on `GET /api/v1/skus` (`page`, `page_size`, `risk`, `ordering`), changing the response shape to `{ results, total, page, page_size, total_pages }`.
- **Hardened action flow** (`feat/harden-action-flow`, PR #14) — adds `pendingSkus`/`bulkPending` in-flight tracking to the store, disables/relabels buttons while a request is pending, blocks double-submit in the action itself (not just the UI), and makes the error banner dismissable.
- **Accessibility + responsive table** (`feat/a11y-responsive-table`, PR #15) — sortable headers are keyboard-operable (`tabindex`, Enter/Space, `aria-sort`), `scope="col"` + a hidden `<caption>`, `aria-pressed` on filter buttons, labeled checkboxes, viewport meta tag. Below 640px the table becomes stacked cards. Note: the responsive `<td>` must stay `display: block`, not `flex`/`grid` — overriding a table cell's display to flex or grid silently drops its text content in this browser (confirmed via isolated repro); the label/value split uses `::before` content instead.

Note: several of these touch the same files (`inventoryStore.js`, `PartsTable.vue`, seed migration) independently of each other — expect merge conflicts if merging more than one before rebasing the others.
