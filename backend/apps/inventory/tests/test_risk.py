from django.test import SimpleTestCase

from apps.inventory.models import SKU
from apps.inventory.services.risk import compute_risk, compute_risk_score
from apps.inventory.services.risk_policy import DEFAULT_POLICY, RiskPolicy, get_policy


class ComputeRiskTests(SimpleTestCase):
    def test_critical_when_projected_stock_is_negative(self):
        # on_hand=1, demand=0.34, lead_time=38 -> projected = 1 - 12.92 = -11.92
        self.assertEqual(compute_risk(1, 0.34, 38, 4), SKU.RISK_CRITICAL)

    def test_warning_when_projected_stock_is_below_safety_stock(self):
        # on_hand=25, demand=2, lead_time=10 -> projected = 5, safety_stock=8
        self.assertEqual(compute_risk(25, 2, 10, 8), SKU.RISK_WARNING)

    def test_ok_when_projected_stock_is_above_safety_stock(self):
        # on_hand=62, demand=1.14, lead_time=14 -> projected = 46.04
        self.assertEqual(compute_risk(62, 1.14, 14, 5), SKU.RISK_OK)

    def test_ok_when_demand_is_zero(self):
        # guards the divide-by-zero / always-flagged trap
        self.assertEqual(compute_risk(179, 0, 41, 0), SKU.RISK_OK)

    def test_ok_exactly_at_safety_stock_boundary(self):
        # projected == safety_stock is the safe side of the boundary
        self.assertEqual(compute_risk(28, 2, 10, 8), SKU.RISK_OK)

    def test_warning_one_unit_below_boundary(self):
        self.assertEqual(compute_risk(27, 2, 10, 8), SKU.RISK_WARNING)

    def test_zero_safety_stock_only_flags_actual_stockout(self):
        # with safety_stock=0 the warning band collapses to "projected < 0"
        self.assertEqual(compute_risk(20, 2, 10, 0), SKU.RISK_OK)
        self.assertEqual(compute_risk(19, 2, 10, 0), SKU.RISK_CRITICAL)


class ComputeRiskScoreTests(SimpleTestCase):
    def test_negative_score_for_at_risk_sku(self):
        score = compute_risk_score(1, 0.34, 38, 4)
        self.assertLess(score, 0)

    def test_positive_score_for_safe_sku(self):
        score = compute_risk_score(62, 1.14, 14, 5)
        self.assertGreater(score, 0)

    def test_zero_demand_scores_as_safe(self):
        score = compute_risk_score(179, 0, 41, 0)
        self.assertGreaterEqual(score, 0)


class RiskPolicyTests(SimpleTestCase):
    def test_default_policy_matches_original_behaviour(self):
        # on_hand=25, demand=2, lead_time=10 -> projected=5, safety_stock=8
        # with default policy (multiplier=1.0): 5 < 8 -> WARNING
        self.assertEqual(
            compute_risk(25, 2, 10, 8, DEFAULT_POLICY),
            SKU.RISK_WARNING,
        )

    def test_strict_policy_warns_earlier(self):
        # same inputs but multiplier=2.0: WARNING if projected < 8*2=16
        # projected=5 < 16 -> still WARNING (no change here)
        # use a case where default is OK but strict is WARNING:
        # on_hand=30, demand=2, lead_time=10 -> projected=10, safety_stock=8
        # default: 10 >= 8 -> OK
        # strict (×2): 10 < 16 -> WARNING
        strict = RiskPolicy(warning_multiplier=2.0)
        self.assertEqual(compute_risk(30, 2, 10, 8), SKU.RISK_OK)
        self.assertEqual(compute_risk(30, 2, 10, 8, strict), SKU.RISK_WARNING)

    def test_get_policy_returns_override_for_known_category(self):
        policy = get_policy("Bearings")
        self.assertGreater(policy.warning_multiplier, 1.0)

    def test_get_policy_falls_back_to_default_for_unknown_category(self):
        self.assertEqual(get_policy("UnknownCategory"), DEFAULT_POLICY)

    def test_custom_critical_threshold(self):
        # raise critical threshold to 5: projected=3 < 5 -> CRITICAL
        # (with default it would be WARNING since 3 >= 0 and 3 < safety_stock=8)
        policy = RiskPolicy(critical_threshold=5.0)
        self.assertEqual(compute_risk(23, 2, 10, 8, policy), SKU.RISK_CRITICAL)
