from django.test import SimpleTestCase

from apps.inventory.models import SKU
from apps.inventory.services.risk import compute_risk, compute_risk_score


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

    def test_exact_score_value(self):
        # projected = 25 - (2 * 10) = 5; score = 5 - 8 = -3
        self.assertAlmostEqual(compute_risk_score(25, 2, 10, 8), -3.0)

    def test_zero_demand_score_equals_safety_stock(self):
        # zero-demand path returns safety_stock directly
        self.assertEqual(compute_risk_score(100, 0, 30, 5), 5)


class ComputeProjectedStockTests(SimpleTestCase):
    def test_basic_projection(self):
        # 50 - (2.0 * 10) = 30
        from apps.inventory.services.risk import compute_projected_stock
        self.assertAlmostEqual(compute_projected_stock(50, 2.0, 10), 30.0)

    def test_negative_projection(self):
        from apps.inventory.services.risk import compute_projected_stock
        self.assertAlmostEqual(compute_projected_stock(5, 1.0, 10), -5.0)

    def test_zero_lead_time(self):
        from apps.inventory.services.risk import compute_projected_stock
        self.assertAlmostEqual(compute_projected_stock(20, 3.5, 0), 20.0)


class ComputeRiskFieldsTests(SimpleTestCase):
    def test_returns_both_fields(self):
        from apps.inventory.services.risk import compute_risk_fields
        result = compute_risk_fields(25, 2, 10, 8)
        self.assertIn("risk", result)
        self.assertIn("risk_score", result)

    def test_fields_are_consistent_with_individual_functions(self):
        from apps.inventory.services.risk import compute_risk_fields
        result = compute_risk_fields(25, 2, 10, 8)
        self.assertEqual(result["risk"], SKU.RISK_WARNING)
        self.assertAlmostEqual(result["risk_score"], -3.0)

    def test_critical_sku_fields(self):
        from apps.inventory.services.risk import compute_risk_fields
        result = compute_risk_fields(1, 0.34, 38, 4)
        self.assertEqual(result["risk"], SKU.RISK_CRITICAL)
        self.assertLess(result["risk_score"], 0)
