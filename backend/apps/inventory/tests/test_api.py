import json

from django.test import SimpleTestCase, TestCase

from apps.inventory.models import SKU
from apps.inventory.services.actions import InvalidActionError, _validate_action


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


class ValidateActionTests(SimpleTestCase):
    def test_none_raises_invalid_action_error(self):
        with self.assertRaises(InvalidActionError):
            _validate_action(None)

    def test_invalid_string_raises_invalid_action_error(self):
        with self.assertRaises(InvalidActionError):
            _validate_action("banana")

    def test_accepted_is_valid(self):
        _validate_action("accepted")  # must not raise

    def test_declined_is_valid(self):
        _validate_action("declined")  # must not raise


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

    def test_invalid_risk_filter_returns_400(self):
        response = self.client.get("/api/v1/skus?risk=banana")
        self.assertEqual(response.status_code, 400)

    def test_invalid_ordering_field_returns_400_not_500(self):
        # Without validation, an unknown field name would crash with a
        # raw 500 (Django raises FieldError when the queryset is
        # evaluated) instead of a clear, frontend-friendly error.
        response = self.client.get("/api/v1/skus?ordering=does_not_exist")
        self.assertEqual(response.status_code, 400)

    def test_descending_ordering_is_accepted(self):
        response = self.client.get("/api/v1/skus?ordering=-on_hand")
        self.assertEqual(response.status_code, 200)


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

    def test_missing_action_returns_400(self):
        make_sku(sku="SP-A")

        response = self.client.post(
            "/api/v1/skus/SP-A/action",
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)


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

    def test_non_list_skus_returns_400(self):
        response = self.client.post(
            "/api/v1/skus/actions",
            data=json.dumps({"skus": "SP-A", "action": "accepted"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_unknown_skus_in_bulk_are_skipped_and_reported(self):
        make_sku(sku="SP-A")

        response = self.client.post(
            "/api/v1/skus/actions",
            data=json.dumps(
                {"skus": ["SP-A", "SP-DOES-NOT-EXIST"], "action": "accepted"}
            ),
            content_type="application/json",
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["updated"], 1)
        self.assertIn("detail", body)

    def test_missing_action_in_bulk_returns_400(self):
        make_sku(sku="SP-A")

        response = self.client.post(
            "/api/v1/skus/actions",
            data=json.dumps({"skus": ["SP-A"]}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_all_unknown_skus_returns_zero_updated(self):
        response = self.client.post(
            "/api/v1/skus/actions",
            data=json.dumps({"skus": ["SP-GHOST-1", "SP-GHOST-2"], "action": "accepted"}),
            content_type="application/json",
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["updated"], 0)
        self.assertIn("detail", body)

    def test_bulk_accepted_updates_status(self):
        make_sku(sku="SP-A")
        make_sku(sku="SP-B")

        response = self.client.post(
            "/api/v1/skus/actions",
            data=json.dumps({"skus": ["SP-A", "SP-B"], "action": "accepted"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["updated"], 2)
        self.assertEqual(SKU.objects.get(sku="SP-A").action_status, "accepted")
        self.assertEqual(SKU.objects.get(sku="SP-B").action_status, "accepted")

    def test_no_detail_key_when_all_skus_found(self):
        make_sku(sku="SP-A")

        response = self.client.post(
            "/api/v1/skus/actions",
            data=json.dumps({"skus": ["SP-A"], "action": "declined"}),
            content_type="application/json",
        )

        self.assertNotIn("detail", response.json())


class ListSkusExtendedTests(TestCase):
    def test_filters_by_warning_risk(self):
        make_sku(sku="SP-W", risk=SKU.RISK_WARNING)
        make_sku(sku="SP-OK", risk=SKU.RISK_OK)

        response = self.client.get("/api/v1/skus?risk=warning")

        skus_in_response = [row["sku"] for row in response.json()]
        self.assertIn("SP-W", skus_in_response)
        self.assertNotIn("SP-OK", skus_in_response)

    def test_filters_by_ok_risk(self):
        make_sku(sku="SP-OK", risk=SKU.RISK_OK)
        make_sku(sku="SP-C", risk=SKU.RISK_CRITICAL)

        response = self.client.get("/api/v1/skus?risk=ok")

        skus_in_response = [row["sku"] for row in response.json()]
        self.assertIn("SP-OK", skus_in_response)
        self.assertNotIn("SP-C", skus_in_response)

    def test_combined_risk_filter_and_ordering(self):
        make_sku(sku="SP-C1", risk=SKU.RISK_CRITICAL, risk_score=-10.0)
        make_sku(sku="SP-C2", risk=SKU.RISK_CRITICAL, risk_score=-5.0)
        make_sku(sku="SP-OK", risk=SKU.RISK_OK)

        response = self.client.get("/api/v1/skus?risk=critical&ordering=risk_score")

        self.assertEqual(response.status_code, 200)
        skus_in_response = [row["sku"] for row in response.json()]
        self.assertNotIn("SP-OK", skus_in_response)
        # SP-C1 has lower score so comes first ascending
        self.assertLess(skus_in_response.index("SP-C1"), skus_in_response.index("SP-C2"))

    def test_ascending_ordering_by_on_hand(self):
        make_sku(sku="SP-LOW", on_hand=1)
        make_sku(sku="SP-HIGH", on_hand=999)

        response = self.client.get("/api/v1/skus?ordering=on_hand")

        self.assertEqual(response.status_code, 200)
        skus = [row["sku"] for row in response.json()]
        self.assertLess(skus.index("SP-LOW"), skus.index("SP-HIGH"))


class SingleActionExtendedTests(TestCase):
    def test_decline_updates_status(self):
        make_sku(sku="SP-A")

        response = self.client.post(
            "/api/v1/skus/SP-A/action",
            data=json.dumps({"action": "declined"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SKU.objects.get(sku="SP-A").action_status, "declined")

    def test_response_body_contains_sku_fields(self):
        make_sku(sku="SP-A")

        response = self.client.post(
            "/api/v1/skus/SP-A/action",
            data=json.dumps({"action": "accepted"}),
            content_type="application/json",
        )

        body = response.json()
        self.assertEqual(body["sku"], "SP-A")
        self.assertIn("risk", body)
        self.assertIn("action_status", body)
        self.assertEqual(body["action_status"], "accepted")

    def test_re_actioning_changes_status(self):
        make_sku(sku="SP-A", action_status=SKU.STATUS_ACCEPTED)

        response = self.client.post(
            "/api/v1/skus/SP-A/action",
            data=json.dumps({"action": "declined"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SKU.objects.get(sku="SP-A").action_status, "declined")
