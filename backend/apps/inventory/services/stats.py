"""
Inventory summary stats for the dashboard KPI cards. Pure aggregation
shaping — the DB work lives in sku_repository; this module just turns
those numbers into the summary shape the API returns.
"""
from apps.inventory.repositories import sku_repository


def compute_summary():
    counts = sku_repository.get_risk_counts()
    critical = counts.get("critical", 0)
    warning = counts.get("warning", 0)
    ok = counts.get("ok", 0)
    total = critical + warning + ok

    # Service level: share of SKUs that are not at risk of stockout.
    # Mirrors PartsOS's "availability / service level" headline metric.
    service_level = round((ok / total) * 100, 1) if total else 0.0

    return {
        "total": total,
        "critical": critical,
        "warning": warning,
        "ok": ok,
        "at_risk_value_eur": sku_repository.get_at_risk_value(),
        "service_level_pct": service_level,
    }
