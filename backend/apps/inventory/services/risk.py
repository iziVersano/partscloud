"""
Stockout risk calculation.

projected = on_hand - (avg_daily_demand * lead_time_days)

  projected < policy.critical_threshold              -> CRITICAL
  projected < safety_stock * policy.warning_multiplier -> WARNING
  otherwise                                          -> OK
  avg_daily_demand == 0                              -> OK (guards the
                                                          divide-by-zero /
                                                          always-critical trap)

risk_score is projected - safety_stock: negative means at risk (more
negative = worse), positive means safe. Used for sorting without
recomputing anything client-side.

Risk is computed once at seed time (see migrations/0002_seed_inventory.py)
and stored on the model. The seed migration inlines the formula rather than
importing this module — see that file's docstring for why.

Pass a RiskPolicy to vary thresholds per category. Omit it (or pass None)
to get the default behaviour, which is identical to the original hardcoded
thresholds.
"""
from apps.inventory.models import SKU
from apps.inventory.services.risk_policy import DEFAULT_POLICY, RiskPolicy, get_policy


def compute_projected_stock(on_hand, avg_daily_demand, lead_time_days):
    return on_hand - (avg_daily_demand * lead_time_days)


def compute_risk(on_hand, avg_daily_demand, lead_time_days, safety_stock, policy: RiskPolicy = None):
    if policy is None:
        policy = DEFAULT_POLICY

    if avg_daily_demand == 0:
        return SKU.RISK_OK

    projected = compute_projected_stock(on_hand, avg_daily_demand, lead_time_days)

    if projected < policy.critical_threshold:
        return SKU.RISK_CRITICAL
    if projected < safety_stock * policy.warning_multiplier:
        return SKU.RISK_WARNING
    return SKU.RISK_OK


def compute_risk_score(on_hand, avg_daily_demand, lead_time_days, safety_stock):
    if avg_daily_demand == 0:
        return float(safety_stock)

    projected = compute_projected_stock(on_hand, avg_daily_demand, lead_time_days)
    return projected - safety_stock


def compute_risk_fields(on_hand, avg_daily_demand, lead_time_days, safety_stock, category: str = ""):
    """Convenience wrapper returning both fields at once.

    Pass category so the correct policy is applied. Used by any code that
    (re)computes risk outside the seed migration.
    """
    policy = get_policy(category)
    return {
        "risk": compute_risk(on_hand, avg_daily_demand, lead_time_days, safety_stock, policy),
        "risk_score": compute_risk_score(on_hand, avg_daily_demand, lead_time_days, safety_stock),
    }
