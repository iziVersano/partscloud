from dataclasses import dataclass


@dataclass(frozen=True)
class RiskPolicy:
    critical_threshold: float = 0.0
    warning_multiplier: float = 1.0


DEFAULT_POLICY = RiskPolicy()

CATEGORY_POLICIES: dict[str, RiskPolicy] = {
    "Bearings": RiskPolicy(warning_multiplier=2.0),  # long lead time, slow to recover
    "Drives": RiskPolicy(warning_multiplier=1.5),    # high unit cost, warn earlier
    "Chains": RiskPolicy(warning_multiplier=1.5),    # failure causes line stoppages
}


def get_policy(category: str) -> RiskPolicy:
    return CATEGORY_POLICIES.get(category, DEFAULT_POLICY)
