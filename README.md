# PartsCloud — Stockout Risk Tracker

Flags spare-part SKUs at risk of running out before the next delivery. Planners can accept or decline per SKU or in bulk.

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Django 5 + Django REST Framework |
| Database | SQLite (file in dev, in-memory in tests) |
| Frontend | Vue 3 (Composition API) + Pinia |
| Build | Vite 5 |
| Tests | pytest-django · Vitest + Vue Test Utils |
| Infra | Docker Compose |

> Page results are not cached client-side; TanStack Query would be the natural next step for stale-while-revalidate caching per page/filter combination.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/iziVersano/partscloud)

---

## Run

```
docker compose up
```

Starts backend `:8000`, frontend `:5173`, and runs the test suite. Migrations and seed data apply automatically on first boot.

**No Docker?** Use the Codespaces badge above — Docker comes preconfigured.

---

## Features

- **Configurable risk policy** — per-category safety-stock multipliers (Bearings ×2.0, Drives/Chains ×1.5) on top of the base risk formula
- **Server-side filtering, sorting, and pagination** — `GET /api/v1/skus` accepts `risk`, `ordering`, `page`, and `page_size`; returns `{results, total, total_pages}`
- **Hardened CSV ingestion** — validates required fields, numeric types, and rejects negative values; bad rows are skipped and reported, not silent failures; `import_skus` management command for re-importing ERP exports
- **Hardened action flow** — per-row and bulk in-flight state; double-submit blocked before the request fires; bulk actions re-fetch from server instead of optimistic updates; errors surface in a dismissable banner
- **Accessibility + responsive** — sortable headers keyboard-operable (Enter/Space), `aria-sort`, `aria-pressed` on filters, `aria-live` regions; stacked card layout below 640px
- **Frontend test layer** — Vitest + Vue Test Utils covering store logic, filtering/sorting, and component interactions (19 tests)

---

## Risk model

```
projected = on_hand - (avg_daily_demand × lead_time_days)
```

| Condition | Risk |
|---|---|
| `projected < 0` | **critical** |
| `projected < safety_stock × category_multiplier` | **warning** |
| otherwise | **ok** |

Zero demand → OK (no stockout risk). Computed once at seed time and stored.

---

## Architecture

**Backend:** `repositories/` (DB) → `services/` (risk + actions, no ORM) → `api/` (thin DRF views)

**Frontend:** feature-based under `features/inventory/` — components, API, and store co-located.

---

## Tests

```
# Backend (52 tests)
python manage.py test apps.inventory --settings=partscloud.settings.test

# Frontend (19 tests)
cd frontend && npm test
```

---

## Checklist

**Backend** — CSV import · risk model · `GET /skus` · accept/decline single + bulk

**Frontend** — risk table · filter/sort · accept/decline single + bulk · pagination

**Ops** — `docker compose up` · Codespaces ready
