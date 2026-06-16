"""
Stockout risk calculation.

projected = on_hand - (avg_daily_demand * lead_time_days)

  projected < 0             -> CRITICAL  (runs out before resupply)
  0 <= projected < safety_stock -> WARNING (breaches the safety cushion)
  projected >= safety_stock  -> OK        (safe)
  avg_daily_demand == 0      -> OK        (can't stock out; guards the
                                            divide-by-zero / always-critical
                                            trap a naive "days of cover"
                                            calculation would hit)

risk_score is projected - safety_stock: negative means at risk (more
negative = worse), positive means safe. It lets the frontend sort by
severity without recomputing anything client-side.

Computed once at seed time (see migrations/0002_seed_inventory.py) and
stored on the model rather than recalculated on every API request.
"""
from apps.inventory.models import SKU


def compute_projected_stock(on_hand, avg_daily_demand, lead_time_days):
    return on_hand - (avg_daily_demand * lead_time_days)


def compute_risk(on_hand, avg_daily_demand, lead_time_days, safety_stock):
    if avg_daily_demand == 0:
        return SKU.RISK_OK

    projected = compute_projected_stock(on_hand, avg_daily_demand, lead_time_days)

    if projected < 0:
        return SKU.RISK_CRITICAL
    if projected < safety_stock:
        return SKU.RISK_WARNING
    return SKU.RISK_OK


def compute_risk_score(on_hand, avg_daily_demand, lead_time_days, safety_stock):
    if avg_daily_demand == 0:
        # No demand means no risk; push it to the safe end of the ranking.
        return safety_stock

    projected = compute_projected_stock(on_hand, avg_daily_demand, lead_time_days)
    return projected - safety_stock


def compute_risk_fields(on_hand, avg_daily_demand, lead_time_days, safety_stock):
    """Convenience wrapper returning both fields at once, used by the
    seed migration when building each row."""
    return {
        "risk": compute_risk(on_hand, avg_daily_demand, lead_time_days, safety_stock),
        "risk_score": compute_risk_score(
            on_hand, avg_daily_demand, lead_time_days, safety_stock
        ),
    }
