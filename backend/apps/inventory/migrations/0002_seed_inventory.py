"""
Loads spare_parts_inventory.csv into the SKU table and computes each
row's risk once, at seed time, rather than on every API request.

Django migrations only ever run once per environment — this is the
"elegant" alternative to a management command with a manual
if-already-seeded guard: migrate is naturally idempotent.
"""
import csv
from pathlib import Path

from django.db import migrations

from apps.inventory.services.risk import compute_risk_fields

CSV_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "spare_parts_inventory.csv"


def load_csv(apps, schema_editor):
    SKU = apps.get_model("inventory", "SKU")

    if SKU.objects.exists():
        return

    rows = []
    with open(CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            on_hand = int(row["on_hand"])
            avg_daily_demand = float(row["avg_daily_demand"])
            lead_time_days = int(row["lead_time_days"])
            safety_stock = int(row["safety_stock"])

            risk_fields = compute_risk_fields(
                on_hand, avg_daily_demand, lead_time_days, safety_stock
            )

            rows.append(
                SKU(
                    sku=row["sku"],
                    name=row["name"],
                    category=row["category"],
                    on_hand=on_hand,
                    avg_daily_demand=avg_daily_demand,
                    lead_time_days=lead_time_days,
                    safety_stock=safety_stock,
                    unit_cost_eur=float(row["unit_cost_eur"]),
                    last_delivery_date=row["last_delivery_date"],
                    risk=risk_fields["risk"],
                    risk_score=risk_fields["risk_score"],
                )
            )

    SKU.objects.bulk_create(rows)


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
