"""
Loads spare_parts_inventory.csv into the SKU table and computes each
row's risk once, at seed time, rather than on every API request.

Django migrations only ever run once per environment — this is the
"elegant" alternative to a management command with a manual
if-already-seeded guard: migrate is naturally idempotent.

NOTE: risk logic and row validation are intentionally inlined here
rather than imported from services/risk.py and services/importer.py.
Django's migration framework executes migrations against historical
model states, and importing live app code in a migration creates a
fragile dependency — if a service signature ever changes, this
historical migration would break. Both are short enough that inlining
is the correct pattern.

A row with a blank/malformed required field or a nonsensical value
(negative stock, negative lead time, etc.) is skipped rather than
crashing the whole seed. Skipped rows are printed so a bad seed file
is noticed, not silently incomplete.
"""
import csv
from pathlib import Path

from django.db import migrations

CSV_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "spare_parts_inventory.csv"

_CATEGORY_WARNING_MULTIPLIERS = {
    "Bearings": 2.0,
    "Drives": 1.5,
    "Chains": 1.5,
}

REQUIRED_TEXT_FIELDS = ["sku", "name", "category", "last_delivery_date"]


def _compute_risk(on_hand, avg_daily_demand, lead_time_days, safety_stock, category):
    """Inlined from services/risk.py — see module docstring for why."""
    if avg_daily_demand == 0:
        return "ok"
    multiplier = _CATEGORY_WARNING_MULTIPLIERS.get(category, 1.0)
    projected = on_hand - (avg_daily_demand * lead_time_days)
    if projected < 0:
        return "critical"
    if projected < safety_stock * multiplier:
        return "warning"
    return "ok"


def _compute_risk_score(on_hand, avg_daily_demand, lead_time_days, safety_stock):
    """Inlined from services/risk.py — see module docstring for why."""
    if avg_daily_demand == 0:
        return float(safety_stock)
    projected = on_hand - (avg_daily_demand * lead_time_days)
    return projected - safety_stock


def _parse_row(row):
    """Inlined from services/importer.py — see module docstring for why."""
    for field_name in REQUIRED_TEXT_FIELDS:
        if not (row.get(field_name) or "").strip():
            raise ValueError(f"{field_name} is blank")

    try:
        on_hand = int(row["on_hand"])
        lead_time_days = int(row["lead_time_days"])
        safety_stock = int(row["safety_stock"])
        avg_daily_demand = float(row["avg_daily_demand"])
        unit_cost_eur = float(row["unit_cost_eur"])
    except (KeyError, ValueError):
        raise ValueError("a numeric field is blank or malformed")

    for field_name, value in (
        ("on_hand", on_hand),
        ("lead_time_days", lead_time_days),
        ("safety_stock", safety_stock),
        ("avg_daily_demand", avg_daily_demand),
        ("unit_cost_eur", unit_cost_eur),
    ):
        if value < 0:
            raise ValueError(f"{field_name} cannot be negative: {value}")

    return {
        "sku": row["sku"].strip(),
        "name": row["name"].strip(),
        "category": row["category"].strip(),
        "on_hand": on_hand,
        "avg_daily_demand": avg_daily_demand,
        "lead_time_days": lead_time_days,
        "safety_stock": safety_stock,
        "unit_cost_eur": unit_cost_eur,
        "last_delivery_date": row["last_delivery_date"].strip(),
    }


def load_csv(apps, schema_editor):
    SKU = apps.get_model("inventory", "SKU")

    if SKU.objects.exists():
        return

    rows = []
    skipped = []
    with open(CSV_PATH, newline="") as f:
        for row_number, row in enumerate(csv.DictReader(f), start=1):
            try:
                parsed = _parse_row(row)
            except ValueError as exc:
                skipped.append((row_number, row.get("sku", "?"), str(exc)))
                continue

            risk_fields = {
                "risk": _compute_risk(
                    parsed["on_hand"], parsed["avg_daily_demand"],
                    parsed["lead_time_days"], parsed["safety_stock"],
                    parsed["category"],
                ),
                "risk_score": _compute_risk_score(
                    parsed["on_hand"], parsed["avg_daily_demand"],
                    parsed["lead_time_days"], parsed["safety_stock"],
                ),
            }

            rows.append(SKU(**parsed, **risk_fields))

    SKU.objects.bulk_create(rows)

    if skipped:
        print(f"WARNING: skipped {len(skipped)} invalid row(s) while seeding inventory:")
        for row_number, sku_code, reason in skipped:
            print(f"  row {row_number} (sku={sku_code}): {reason}")


def unload_csv(apps, schema_editor):
    SKU = apps.get_model("inventory", "SKU")
    SKU.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_create_sku_table"),
    ]

    operations = [
        migrations.RunPython(load_csv, reverse_code=unload_csv),
    ]
