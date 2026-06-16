# PartsCloud — Stockout Risk Tracker

Flags spare-part SKUs at risk of running out before the next delivery,
and lets a planner accept or decline the suggestion per SKU or in bulk.

## Run it — one command

```
docker compose up
```

That single command builds and starts both containers — nothing else
to install or configure first.

```
                docker compose up
                       │
        ┌──────────────┴──────────────┐
        ▼                              ▼
┌───────────────────┐        ┌───────────────────┐
│  backend (Django)  │        │  frontend (Vue)    │
│  :8000              │◄──────│  :5173, proxies    │
│                     │  API  │  /api → backend     │
│  migrate → seed CSV │       │                     │
│  → serve API        │       └───────────────────┘
└───────────────────┘
        │
        ▼
   open http://localhost:5173 in a browser
```

- API: http://localhost:8000/api/v1/skus
- UI: http://localhost:5173

On first boot, `migrate` creates the schema and loads the CSV into
SQLite as a data migration — no separate seed step. Migrations only
run once, so restarting the containers won't duplicate rows.

## How I defined "at risk"

```
projected = on_hand - (avg_daily_demand × lead_time_days)
```

That's: how many units are left when the next delivery actually
arrives, at normal selling pace. I flag against two lines:

- `projected < 0` → **critical** — runs out before resupply.
- `projected < safety_stock` → **warning** — survives, but eats into
  the buffer the customer set aside for spikes or late deliveries.
- otherwise → **ok**.

I flag at the safety-stock line, not zero, because the buffer only
helps if there's still lead time left to react when you breach it —
waiting for zero means the wait has already started with no margin.

```
on_hand, avg_daily_demand, lead_time_days, safety_stock
                    │
                    ▼
        avg_daily_demand == 0 ? ──yes──► OK (can't stock out)
                    │ no
                    ▼
projected = on_hand − (avg_daily_demand × lead_time_days)
                    │
        ┌───────────┼───────────────┐
        ▼           ▼               ▼
  projected<0   projected<safety   else
        │              │             │
        ▼              ▼             ▼
   CRITICAL        WARNING          OK
```

Two edge cases the data plants: zero demand (divides by zero in a naive
calc — treated as safe, since it can't stock out) and zero safety stock
(the warning band collapses, so only an actual stockout flags — correct,
not a bug). Both are tested.

Risk is computed once at seed time and stored, not recalculated per
request — it only depends on data that doesn't change in this scope.

## Why this structure

I split the backend into `repositories/` (DB access), `services/`
(risk + accept/decline logic), and `api/` (thin views that just call
a service and return). 50 rows doesn't need this — the reason I did it
anyway is the risk formula is the one thing I most expect to be asked
to change live, and with it isolated from Django/HTTP it's a plain
function I can edit and re-test in seconds, not something tangled into
a view. Settings are split by environment for the same instinct: cheap
to set up now, saves a rewrite if this ever needs Postgres.

Frontend is organized by feature (`features/inventory/` holds its own
components, API calls, and store) rather than by file type, so a
second feature wouldn't mean spreading new files across existing
folders.

None of this is required for a 50-row task — I'd be just as happy
explaining a flatter version. I chose it because it's what I'd reach
for the moment a second feature or a second developer showed up, and
it cost nothing extra to set up correctly from the start.

## What I chose not to build

- **Order quantities** — the brief asks "is this at risk," not "how
  much to reorder." That needs a max-stock/EOQ policy the data doesn't
  give me.
- **Caching** — not a real problem at this scale; I'd add it with
  thousands of SKUs and concurrent planners.
- **Frontend tests** — backend has unit tests on the risk function
  (including both edge cases) and integration tests on all three
  endpoints; Vue testing needed a setup step I didn't think was worth
  the time box.
- **Auth** — anyone with the URL can accept/decline. Fine here, not in
  production.

## With more time

Postgres + background risk recomputation if `on_hand` changes outside
the seed step; an actual order-quantity suggestion once a replenishment
policy exists; frontend tests; a real design pass on the UI.
