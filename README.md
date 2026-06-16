# PartsCloud — Stockout Risk Tracker

A small service that flags spare-part SKUs at risk of running out before
the next delivery, and lets a planner accept or decline the suggestion
per SKU or in bulk.

## How to run it

```
docker compose up
```

- Backend (Django + DRF): http://localhost:8000/api/v1/skus
- Frontend (Vue): http://localhost:5173

On first boot, Django's `migrate` command creates the schema and loads
`spare_parts_inventory.csv` into SQLite as part of a data migration.
Migrations are idempotent, so restarting the containers does not
re-seed or duplicate rows.

No separate setup step is needed — the CSV → DB load is part of
`migrate`, which the backend container runs automatically before
starting the server.

## How I defined "at risk"

For each SKU, I project stock forward across its own lead time:

```
projected = on_hand - (avg_daily_demand × lead_time_days)
```

This is "how many units will be left when the next delivery actually
arrives, if I keep selling at my normal rate." I classify against two
lines, not one:

- `projected < 0` → **critical** — an actual stockout before resupply.
- `0 ≤ projected < safety_stock` → **warning** — survives, but eats into
  the buffer the customer explicitly set aside for demand spikes or late
  deliveries.
- `projected ≥ safety_stock` → **ok**.

I flag at the safety-stock line rather than waiting for zero because the
buffer only protects you if you still have lead time left to react when
you breach it — alarming at zero means the 10+ day wait has already
started with no margin.

Two edge cases the data deliberately includes:
- `avg_daily_demand == 0` (SP-1002) — a naive day-of-cover calculation
  divides by zero or returns "always critical." I treat zero demand as
  inherently safe.
- `safety_stock == 0` (several SKUs) — the warning band collapses, so
  only an actual projected stockout flags. That's intentional, not a bug.

I also compute a `risk_score` (`projected - safety_stock`) alongside the
label, so severity can be sorted/ranked rather than just bucketed.

Both fields are computed **once**, in the seed migration — not
recalculated on every API request — since they only depend on data
that doesn't change after seeding in this scope.

## Architecture

Backend follows a thin-views / fat-services split with a repository
layer between services and the ORM:

```
apps/inventory/
  models.py        SKU table
  repositories/     all direct DB access
  services/         risk.py (the formula), actions.py (accept/decline)
  api/v1/           HTTP layer only — parses requests, calls services
  migrations/        schema + the CSV seed
```

This isn't necessary at 50 rows, but it means the risk logic and the
accept/decline logic are unit-testable without HTTP, and a future second
domain (e.g. suppliers) becomes a new app under `apps/` rather than more
files crammed into this one. Settings are split by environment
(`base/dev/prod/test`) for the same reason — `prod.py` isn't wired up
anywhere yet, but the seam exists.

Frontend is feature-based rather than type-based: everything about the
inventory feature (components, API client, Pinia store) lives under
`features/inventory/`, so a second feature wouldn't mean reorganizing
existing folders.

## What I chose not to build

- **Order quantities.** The brief asks "is this at risk," not "how much
  should we reorder" — that needs a max-stock or EOQ policy the data
  doesn't provide, so I stopped at flagging risk.
- **Caching.** 50 rows and a subtraction is not a performance problem.
  I'd only add it if this were serving thousands of SKUs to many
  concurrent planners.
- **Frontend tests.** Backend has unit tests on the risk function
  (including both edge cases) and integration tests on all three
  endpoints. Vue component testing needs a Jest/Vitest setup that felt
  out of scope for the time box.
- **Auth.** Anyone with the URL can accept/decline. Fine for a take-home,
  not for production.

## What I'd do differently with more time

- Swap SQLite for PostgreSQL and move risk computation to a background
  job if SKU volume grew — currently it's computed once at seed time,
  which is fine at this scale but wouldn't refresh if `on_hand` changed
  via some other process.
- Add the missing piece for a real workflow: an order-quantity
  suggestion, once a replenishment policy is defined.
- Frontend tests, and a proper design pass on the UI — it's functional,
  not polished, by design given the time box.
