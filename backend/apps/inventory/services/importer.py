from dataclasses import dataclass
from datetime import datetime


@dataclass
class RowError:
    row_number: int
    sku: str
    reason: str


@dataclass
class ImportResult:
    rows: list
    errors: list


def _required_text(row, field_name):
    value = (row.get(field_name) or "").strip()
    if not value:
        raise ValueError(f"{field_name} is blank")
    return value


def _parse_int(row, field_name):
    raw = (row.get(field_name) or "").strip()
    if not raw:
        raise ValueError(f"{field_name} is blank")
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(f"{field_name} is not a valid integer: {raw!r}")
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative: {value}")
    return value


def _parse_float(row, field_name):
    raw = (row.get(field_name) or "").strip()
    if not raw:
        raise ValueError(f"{field_name} is blank")
    try:
        value = float(raw)
    except ValueError:
        raise ValueError(f"{field_name} is not a valid number: {raw!r}")
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative: {value}")
    return value


def _parse_date(row, field_name):
    raw = (row.get(field_name) or "").strip()
    if not raw:
        raise ValueError(f"{field_name} is blank")
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"{field_name} is not a valid date (expected YYYY-MM-DD): {raw!r}")


def parse_row(row: dict) -> dict:
    return {
        "sku": _required_text(row, "sku"),
        "name": _required_text(row, "name"),
        "category": _required_text(row, "category"),
        "on_hand": _parse_int(row, "on_hand"),
        "avg_daily_demand": _parse_float(row, "avg_daily_demand"),
        "lead_time_days": _parse_int(row, "lead_time_days"),
        "safety_stock": _parse_int(row, "safety_stock"),
        "unit_cost_eur": _parse_float(row, "unit_cost_eur"),
        "last_delivery_date": _parse_date(row, "last_delivery_date"),
    }


def import_rows(csv_rows) -> ImportResult:
    rows = []
    errors = []
    for row_number, row in enumerate(csv_rows, start=1):
        try:
            rows.append(parse_row(row))
        except ValueError as exc:
            errors.append(
                RowError(row_number=row_number, sku=row.get("sku", "?"), reason=str(exc))
            )
    return ImportResult(rows=rows, errors=errors)
