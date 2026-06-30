import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.inventory.models import SKU
from apps.inventory.services.importer import import_rows
from apps.inventory.services.risk import compute_risk_fields


class Command(BaseCommand):
    help = "Import SKUs from a CSV file, skipping and reporting invalid rows."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        try:
            f = open(csv_path, newline="")
        except OSError as exc:
            raise CommandError(f"Could not open {csv_path}: {exc}")

        with f:
            result = import_rows(csv.DictReader(f))

        with transaction.atomic():
            for row in result.rows:
                risk_fields = compute_risk_fields(
                    row["on_hand"],
                    row["avg_daily_demand"],
                    row["lead_time_days"],
                    row["safety_stock"],
                    category=row.get("category", ""),
                )
                SKU.objects.update_or_create(
                    sku=row["sku"],
                    defaults={**row, **risk_fields},
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(result.rows)} row(s); skipped {len(result.errors)}."
            )
        )
        for err in result.errors:
            self.stdout.write(
                self.style.WARNING(f"  row {err.row_number} (sku={err.sku}): {err.reason}")
            )
