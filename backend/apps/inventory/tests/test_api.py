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

        response = self.client.get("/api/v1/skus?page_size=100")

        skus_in_response = [row["sku"] for row in response.json()["results"]]
        self.assertEqual(response.status_code, 200)
        self.assertIn("SP-A", skus_in_response)

    def test_filters_by_risk(self):
        make_sku(sku="SP-TEST-CRITICAL", risk=SKU.RISK_CRITICAL)
        make_sku(sku="SP-TEST-OK", risk=SKU.RISK_OK)

        response = self.client.get("/api/v1/skus?risk=critical&page_size=100")

        skus_in_response = [row["sku"] for row in response.json()["results"]]
        self.assertIn("SP-TEST-CRITICAL", skus_in_response)
        self.assertNotIn("SP-TEST-OK", skus_in_response)

    def test_invalid_risk_filter_returns_400(self):
        response = self.client.get("/api/v1/skus?risk=banana")
        self.assertEqual(response.status_code, 400)

    def test_filters_by_comma_separated_risk_values(self):
        make_sku(sku="SP-TEST-CRIT2", risk=SKU.RISK_CRITICAL)
        make_sku(sku="SP-TEST-WARN2", risk=SKU.RISK_WARNING)
        make_sku(sku="SP-TEST-OK2", risk=SKU.RISK_OK)

        response = self.client.get("/api/v1/skus?risk=critical,warning&page_size=100")

        skus_in_response = [row["sku"] for row in response.json()["results"]]
        self.assertIn("SP-TEST-CRIT2", skus_in_response)
        self.assertIn("SP-TEST-WARN2", skus_in_response)
        self.assertNotIn("SP-TEST-OK2", skus_in_response)

    def test_comma_separated_risk_with_one_invalid_value_returns_400(self):
        response = self.client.get("/api/v1/skus?risk=critical,banana")
        self.assertEqual(response.status_code, 400)

    def test_search_matches_sku_code(self):
        make_sku(sku="SP-FINDME", name="Irrelevant name")

        response = self.client.get("/api/v1/skus?search=FINDME&page_size=100")

        skus_in_response = [row["sku"] for row in response.json()["results"]]
        self.assertIn("SP-FINDME", skus_in_response)

    def test_search_matches_name_case_insensitively(self):
        make_sku(sku="SP-NAMETEST", name="Special Widget Assembly")

        response = self.client.get("/api/v1/skus?search=widget&page_size=100")

        skus_in_response = [row["sku"] for row in response.json()["results"]]
        self.assertIn("SP-NAMETEST", skus_in_response)

    def test_search_excludes_non_matching_rows(self):
        make_sku(sku="SP-EXCLUDE1", name="Totally unrelated part")

        response = self.client.get("/api/v1/skus?search=zzz-no-match-zzz")

        skus_in_response = [row["sku"] for row in response.json()["results"]]
        self.assertNotIn("SP-EXCLUDE1", skus_in_response)

    def test_invalid_ordering_field_returns_400_not_500(self):
        # Without validation, an unknown field name would crash with a
        # raw 500 (Django raises FieldError when the queryset is
        # evaluated) instead of a clear, frontend-friendly error.
        response = self.client.get("/api/v1/skus?ordering=does_not_exist")
        self.assertEqual(response.status_code, 400)

    def test_descending_ordering_is_accepted(self):
        response = self.client.get("/api/v1/skus?ordering=-on_hand")
        self.assertEqual(response.status_code, 200)

    def test_pagination_defaults_to_page_size_10(self):
        for i in range(15):
            make_sku(sku=f"SP-PAGE-{i}")

        response = self.client.get("/api/v1/skus")
        body = response.json()

        self.assertEqual(len(body["results"]), 10)
        self.assertEqual(body["page"], 1)
        self.assertEqual(body["page_size"], 10)
        self.assertGreaterEqual(body["total"], 15)

    def test_page_param_returns_next_page(self):
        for i in range(15):
            make_sku(sku=f"SP-NEXT-{i}")

        first_page = self.client.get("/api/v1/skus?page_size=10").json()
        second_page = self.client.get("/api/v1/skus?page=2&page_size=10").json()

        first_skus = {row["sku"] for row in first_page["results"]}
        second_skus = {row["sku"] for row in second_page["results"]}
        self.assertEqual(first_skus & second_skus, set())

    def test_page_size_is_capped_at_100(self):
        response = self.client.get("/api/v1/skus?page_size=500")
        self.assertEqual(response.json()["page_size"], 100)

    def test_invalid_page_returns_400(self):
        response = self.client.get("/api/v1/skus?page=not-a-number")
        self.assertEqual(response.status_code, 400)


class StatsTests(TestCase):
    def test_returns_expected_shape(self):
        response = self.client.get("/api/v1/skus/stats")
        body = response.json()

        self.assertEqual(response.status_code, 200)
        for key in ("total", "critical", "warning", "ok", "at_risk_value_eur", "service_level_pct"):
            self.assertIn(key, body)

    def test_counts_reflect_created_skus(self):
        before = self.client.get("/api/v1/skus/stats").json()

        make_sku(sku="SP-STATS-CRIT", risk=SKU.RISK_CRITICAL, on_hand=10, unit_cost_eur=5)
        make_sku(sku="SP-STATS-OK", risk=SKU.RISK_OK)

        after = self.client.get("/api/v1/skus/stats").json()

        self.assertEqual(after["critical"], before["critical"] + 1)
        self.assertEqual(after["ok"], before["ok"] + 1)
        self.assertEqual(after["total"], before["total"] + 2)

    def test_at_risk_value_includes_critical_and_warning_only(self):
        before = self.client.get("/api/v1/skus/stats").json()

        make_sku(sku="SP-STATS-ATRISK", risk=SKU.RISK_CRITICAL, on_hand=10, unit_cost_eur=5)
        make_sku(sku="SP-STATS-SAFE", risk=SKU.RISK_OK, on_hand=1000, unit_cost_eur=1000)

        after = self.client.get("/api/v1/skus/stats").json()

        # Only the critical SKU's value (10 * 5 = 50) should be added — the OK
        # SKU, despite being far more valuable, must not count as "at risk".
        self.assertAlmostEqual(
            after["at_risk_value_eur"] - before["at_risk_value_eur"], 50.0
        )

    def test_service_level_is_percentage_of_ok_skus(self):
        body = self.client.get("/api/v1/skus/stats").json()

        self.assertGreaterEqual(body["service_level_pct"], 0)
        self.assertLessEqual(body["service_level_pct"], 100)


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

    def test_duplicate_sku_in_request_is_not_reported_as_skipped(self):
        # Regression test: Django's .update() returns the count of
        # distinct rows matched, not the number of entries in the
        # request list. A duplicate SKU id in the same bulk request
        # (e.g. a double-click sending the same id twice) must not be
        # misreported as "skipped".
        make_sku(sku="SP-A")

        response = self.client.post(
            "/api/v1/skus/actions",
            data=json.dumps(
                {"skus": ["SP-A", "SP-A"], "action": "accepted"}
            ),
            content_type="application/json",
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["updated"], 1)
        self.assertNotIn("detail", body)
