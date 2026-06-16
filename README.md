# PartsCloud — Stockout Risk Tracker

Flags spare-part SKUs at risk of running out before the next delivery,
and lets a planner accept or decline the suggestion per SKU or in bulk.

**Stack:** Django · DRF · SQLite · Vue 3 · Pinia · Docker Compose

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/iziVersano/partscloud)

---

## Run it — one command

```
docker compose up
```

```
             docker compose up
           |                       |
           +-----------------------+
           v                       v
+--------------------+    +----------------+
|  backend (Django)  |    | frontend (Vue) |
|       :8000        | <--|     :5173      |
| migrate + seed CSV |    |  proxies /api  |
+--------------------+    +----------------+
```

| Service | URL |
|---|---|
| API | http://localhost:8000/api/v1/skus |
| UI | http://localhost:5173 |

`migrate` creates the schema and seeds the CSV in one step on first
boot. It's a data migration, so it only runs once — restarting won't
duplicate rows.

**No Docker locally?** Click the badge above (or **Code** → **Codespaces**
→ **Create codespace on main**) — Docker comes preconfigured via
`.devcontainer/`, no local setup needed:

1. Wait for the codespace to build (sets up Docker automatically)
2. In the terminal that opens: `docker compose up`
3. Click the **port 5173** notification/link to open the UI

## Tests

`docker compose up` runs the test suite automatically, in its own
`tests` container — no separate command needed. It starts once the
backend container is up and exits when done (usually within a second,
since it's just 23 tests against an in-memory DB); its output appears
in the logs alongside backend and frontend, and it doesn't block or
affect the running app either way.

To re-run them on demand without restarting everything:

```
docker compose exec backend python manage.py test apps.inventory --settings=partscloud.settings.test
```

23 tests — risk function (including both edge cases) and all three API
endpoints, against an in-memory DB.

---

## How I defined "at risk"

```
projected = on_hand - (avg_daily_demand x lead_time_days)
```

Units left when the next delivery arrives, at normal selling pace:

| Condition | Risk |
|---|---|
| `projected < 0` | **critical** — runs out before resupply |
| `projected < safety_stock` | **warning** — eats into the buffer meant for spikes or late deliveries |
| otherwise | **ok** |

I flag at the safety-stock line, not zero — the buffer only helps if
there's still lead time left to react when you breach it.

```
             avg_daily_demand == 0?
 yes --> OK (treated as safe, can't stock out)
                       no
                       v
projected = on_hand - (demand x lead_time_days)
                       |
      +---------------------+----------------+
      v                     v                v
projected < 0   projected < safety_stock   else
   CRITICAL             WARNING             OK
```

Two tested edge cases: zero demand (would divide by zero — treated as
safe) and zero safety stock (warning band collapses to "stockout only" —
correct, not a bug). Risk is computed once at seed time and stored, not
recalculated per request.

---

## Why this structure

**Backend:** `repositories/` (DB access) → `services/` (risk +
accept/decline logic — plain functions, no ORM or HTTP inside them) →
`api/` (thin Django/DRF views). The risk formula is what I most expect
to be asked to change live, so it's isolated and unit-testable in
seconds, not tangled into a view.

```
views.py (thin) -> services/ (the logic) -> repositories/ (only ORM contact) -> SQLite
```

**Frontend:** feature-based, not type-based — `features/inventory/`
holds its own components, API calls, and store, so a second feature is
a sibling folder, not files scattered into shared ones.

```
src/
|-- router/, shared/components/, shared/composables/   (empty, reserved)
`-- features/inventory/  -> components/, api/, store/
```

Not required at 50 rows — I'd happily explain a flatter version. I'd
reach for this the moment a second feature or developer showed up, and
it cost nothing to set up correctly now.

---

## Error handling

Catch specific, expected failures → clear 4xx; anything else is a real
500, not silently disguised.

- `ordering`/`risk` query params are validated (an unknown field used
  to crash with a raw 500)
- unknown SKU is `SKU.DoesNotExist`, not a blanket `except Exception`
  masking real bugs as 404
- bulk actions report any SKUs skipped rather than going silent

---

## What I chose not to build

- **Order quantities** — brief asks "at risk," not "how much to
  reorder"; needs a policy the data doesn't give me
- **Caching** — not a real problem at 50 rows
- **Frontend tests** — backend has unit + integration tests; Vue
  testing needed setup I didn't think worth the time box
- **Auth** — fine for a take-home, not production

## With more time

Postgres + background risk recompute if `on_hand` changes; an actual
order-quantity suggestion; frontend tests; a real design pass.

---

## Requirements checklist

**Backend**
- [x] CSV → DB
- [x] risk per SKU
- [x] `GET /skus`
- [x] accept/decline single + bulk

**Frontend**
- [x] list with risk indicator
- [x] filter/sort
- [x] accept/decline single + bulk

**Ops**
- [x] `docker compose up` (local or Codespace)

**README**
- [x] how to run
- [x] risk definition + why
- [x] what's skipped + why
- [x] what I'd do with more time
