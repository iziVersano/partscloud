"""
Risk policies control the thresholds used by compute_risk().

Each policy has two knobs:

  critical_threshold   — projected stock below this value → CRITICAL.
                         Default is 0 (runs out before resupply arrives).

  warning_multiplier   — WARNING if projected stock < safety_stock × multiplier.
                         Default is 1.0 (standard safety-stock boundary).
                         Values above 1.0 create an earlier warning band,
                         useful for categories with long or unreliable lead times.

CATEGORY_POLICIES maps category names to their policy. Any category not listed
falls back to DEFAULT_POLICY, which reproduces the original hardcoded behaviour.

On fields not currently used in the formula:

  unit_cost_eur       — A high-cost part stocking out is more expensive, but
                        folding cost into the risk level makes it harder to
                        reason about. It is available for a policy to express
                        (e.g. stricter warning for Drives which average €300+)
                        via warning_multiplier rather than a cost branch.

  last_delivery_date  — Could signal supplier reliability, but without a
                        baseline lead-time-vs-actual-delivery comparison in
                        this dataset it would add noise rather than signal.
                        Left out until that data is available.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RiskPolicy:
    critical_threshold: float = 0.0
    warning_multiplier: float = 1.0


DEFAULT_POLICY = RiskPolicy()

# Per-category overrides — categories not listed here use DEFAULT_POLICY.
CATEGORY_POLICIES: dict[str, RiskPolicy] = {
    # 41-day lead time makes stockouts hard to recover from quickly.
    "Bearings": RiskPolicy(warning_multiplier=2.0),
    # Drives are high-cost (avg ~€300+); warn earlier to reduce exposure.
    "Drives": RiskPolicy(warning_multiplier=1.5),
    # Chains have moderate lead times and failure causes line stoppages.
    "Chains": RiskPolicy(warning_multiplier=1.5),
}


def get_policy(category: str) -> RiskPolicy:
    return CATEGORY_POLICIES.get(category, DEFAULT_POLICY)
