import importlib

from django.test import SimpleTestCase

from apps.inventory.services.importer import import_rows, parse_row

_seed_migration = importlib.import_module("apps.inventory.migrations.0002_seed_inventory")


def make_row(**overrides):
    defaults = dict(
        sku="SP-1001",
        name="Hydraulic seal kit, 50mm",
        category="Seals",
        on_hand="62",
        avg_daily_demand="1.14",
        lead_time_days="14",
        safety_stock="5",
        unit_cost_eur="41.73",
        last_delivery_date="2026-03-10",
    )
    defaults.update(overrides)
    return defaults


class ParseRowTests(SimpleTestCase):
    def test_valid_row_parses_correctly(self):
        parsed = parse_row(make_row())
        self.assertEqual(parsed["sku"], "SP-1001")
        self.assertEqual(parsed["on_hand"], 62)
        self.assertEqual(parsed["avg_daily_demand"], 1.14)
        self.assertEqual(parsed["last_delivery_date"].isoformat(), "2026-03-10")

    def test_blank_required_text_field_raises(self):
        with self.assertRaises(ValueError):
            parse_row(make_row(sku=""))

    def test_blank_numeric_field_raises(self):
        with self.assertRaises(ValueError):
            parse_row(make_row(on_hand=""))

    def test_malformed_numeric_field_raises(self):
        with self.assertRaises(ValueError):
            parse_row(make_row(on_hand="not-a-number"))

    def test_negative_on_hand_raises(self):
        with self.assertRaises(ValueError):
            parse_row(make_row(on_hand="-5"))

    def test_negative_lead_time_raises(self):
        with self.assertRaises(ValueError):
            parse_row(make_row(lead_time_days="-1"))

    def test_negative_safety_stock_raises(self):
        with self.assertRaises(ValueError):
            parse_row(make_row(safety_stock="-1"))

    def test_negative_avg_daily_demand_raises(self):
        with self.assertRaises(ValueError):
            parse_row(make_row(avg_daily_demand="-0.5"))

    def test_malformed_date_raises(self):
        with self.assertRaises(ValueError):
            parse_row(make_row(last_delivery_date="not-a-date"))

    def test_whitespace_only_field_raises(self):
        with self.assertRaises(ValueError):
            parse_row(make_row(category="   "))


class ImportRowsTests(SimpleTestCase):
    def test_valid_rows_all_imported(self):
        result = import_rows([make_row(sku="SP-A"), make_row(sku="SP-B")])
        self.assertEqual(len(result.rows), 2)
        self.assertEqual(len(result.errors), 0)

    def test_bad_row_is_skipped_not_fatal(self):
        result = import_rows(
            [make_row(sku="SP-A"), make_row(sku="SP-BAD", on_hand="-5"), make_row(sku="SP-C")]
        )
        self.assertEqual(len(result.rows), 2)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].sku, "SP-BAD")
        self.assertEqual(result.errors[0].row_number, 2)

    def test_error_reason_is_descriptive(self):
        result = import_rows([make_row(on_hand="garbage")])
        self.assertIn("on_hand", result.errors[0].reason)


class SeedMigrationValidationTests(SimpleTestCase):
    def test_valid_row_parses(self):
        parsed = _seed_migration._parse_row(make_row())
        self.assertEqual(parsed["sku"], "SP-1001")

    def test_blank_field_raises(self):
        with self.assertRaises(ValueError):
            _seed_migration._parse_row(make_row(sku=""))

    def test_malformed_number_raises(self):
        with self.assertRaises(ValueError):
            _seed_migration._parse_row(make_row(on_hand="not-a-number"))

    def test_negative_value_raises(self):
        with self.assertRaises(ValueError):
            _seed_migration._parse_row(make_row(on_hand="-5"))
