import json

from django.test import TestCase

from apps.inventory.models import SKU


def make_sku(**overrides):
    defaults = dict(
        sku="SP-9999",
        name="Test part",
        category="Test",
        on_hand=10,
        avg_daily_demand=1.0,
        lead_time_days=5,
        safety_stock=2,
        unit_cost_eur=9.99,
        last_delivery_date="2026-01-01",
        risk=SKU.RISK_OK,
        risk_score=3.0,
    )
    defaults.update(overrides)
    return SKU.objects.create(**defaults)


class ListSkusTests(TestCase):
    def test_returns_created_sku_among_results(self):
        # The seed migration runs against the test DB too, so we don't
        # assert a total count — we assert our SKU is present.
        make_sku(sku="SP-A")

        response = self.client.get("/api/v1/skus")

        skus_in_response = [row["sku"] for row in response.json()]
        self.assertEqual(response.status_code, 200)
        self.assertIn("SP-A", skus_in_response)

    def test_filters_by_risk(self):
        make_sku(sku="SP-TEST-CRITICAL", risk=SKU.RISK_CRITICAL)
        make_sku(sku="SP-TEST-OK", risk=SKU.RISK_OK)

        response = self.client.get("/api/v1/skus?risk=critical")

        skus_in_response = [row["sku"] for row in response.json()]
        self.assertIn("SP-TEST-CRITICAL", skus_in_response)
        self.assertNotIn("SP-TEST-OK", skus_in_response)


class SingleActionTests(TestCase):
    def test_accept_updates_status(self):
        make_sku(sku="SP-A")

        response = self.client.post(
            "/api/v1/skus/SP-A/action",
            data=json.dumps({"action": "accepted"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SKU.objects.get(sku="SP-A").action_status, "accepted")

    def test_invalid_action_returns_400(self):
        make_sku(sku="SP-A")

        response = self.client.post(
            "/api/v1/skus/SP-A/action",
            data=json.dumps({"action": "banana"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_unknown_sku_returns_404(self):
        response = self.client.post(
            "/api/v1/skus/SP-DOES-NOT-EXIST/action",
            data=json.dumps({"action": "accepted"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)


class BulkActionTests(TestCase):
    def test_bulk_decline_updates_all_selected(self):
        make_sku(sku="SP-A")
        make_sku(sku="SP-B")
        make_sku(sku="SP-C")

        response = self.client.post(
            "/api/v1/skus/actions",
            data=json.dumps({"skus": ["SP-A", "SP-B"], "action": "declined"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["updated"], 2)
        self.assertEqual(SKU.objects.get(sku="SP-A").action_status, "declined")
        self.assertEqual(SKU.objects.get(sku="SP-B").action_status, "declined")
        self.assertEqual(SKU.objects.get(sku="SP-C").action_status, "pending")

    def test_empty_sku_list_returns_400(self):
        response = self.client.post(
            "/api/v1/skus/actions",
            data=json.dumps({"skus": [], "action": "accepted"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
