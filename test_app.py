"""Automated tests for Esports IQ database and validation."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from data_layer import (
    init_db,
    save_dataset,
    load_latest_dataset,
    validate_required_columns,
    validate_prepared_data,
    log_event,
    recent_audit_events,
)


class TestEsportsIQ(unittest.TestCase):

    def setUp(self):
            self.temp_dir = tempfile.TemporaryDirectory()
            self.db_path = Path(self.temp_dir.name) / "test_esports_iq.db"
            init_db(self.db_path)

    def tearDown(self):
        import gc
        import sqlite3

        gc.collect()

        for suffix in ("", "-wal", "-shm"):
            file_path = Path(str(self.db_path) + suffix)
            if file_path.exists():
                try:
                    file_path.unlink()
                except PermissionError:
                    pass

        self.temp_dir.cleanup()

    def sample_data(self):
            return pd.DataFrame({
            "shop_name": ["Ace Sports Hub", "Elite Sports"],
            "product_name": ["Cricket Bat", "Football"],
            "category": ["Cricket", "Football"],
            "units_sold": [10, 5],
            "unit_price": [1500, 800],
            "stock_qty": [20, 15],
        })

    def test_database_tables_are_created(self):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        try:
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
        finally:
            conn.close()

        self.assertIn("dataset_versions", tables)
        self.assertIn("audit_events", tables)

    def test_dataset_can_be_saved_and_loaded(self):
        original = self.sample_data()

        save_dataset(original, "test_data.xlsx", self.db_path)
        loaded, metadata = load_latest_dataset(self.db_path)

        self.assertIsNotNone(loaded)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(metadata["filename"], "test_data.xlsx")
        self.assertEqual(metadata["row_count"], 2)
        self.assertEqual(
            loaded["product_name"].tolist(),
            original["product_name"].tolist(),
        )

    def test_empty_database_returns_no_dataset(self):
        loaded, metadata = load_latest_dataset(self.db_path)

        self.assertIsNone(loaded)
        self.assertIsNone(metadata)

    def test_missing_required_columns_are_detected(self):
        df = pd.DataFrame({
            "shop_name": ["Ace Sports Hub"],
            "product_name": ["Cricket Bat"],
        })

        missing = validate_required_columns(df)

        self.assertIn("category", missing)
        self.assertIn("unit_price", missing)

    def test_valid_data_passes_validation(self):
        errors = validate_prepared_data(self.sample_data())

        self.assertEqual(errors, [])

    def test_negative_values_are_rejected(self):
        df = self.sample_data()
        df.loc[0, "units_sold"] = -5

        errors = validate_prepared_data(df)

        self.assertTrue(
            any("negative" in error.lower() for error in errors)
        )

    def test_audit_events_are_saved(self):
        log_event(
            username="test_user",
            role="admin",
            shop="Ace Sports Hub",
            action="test_action",
            db_path=self.db_path,
        )

        events = recent_audit_events(db_path=self.db_path)

        self.assertEqual(len(events), 1)
        self.assertEqual(events.iloc[0]["username"], "test_user")
        self.assertEqual(events.iloc[0]["action"], "test_action")


    def test_missing_numeric_values_are_rejected(self):
        df = self.sample_data()
        df.loc[0, "units_sold"] = None

        errors = validate_prepared_data(df)

        self.assertTrue(
            any("missing or non-numeric" in error.lower() for error in errors)
        )

    def test_invalid_dates_are_rejected(self):
        df = self.sample_data()
        df["date"] = ["invalid-date", "also-invalid"]

        errors = validate_prepared_data(df)

        self.assertTrue(
            any("no valid dates" in error.lower() for error in errors)
        )

        
if __name__ == "__main__":
    unittest.main(verbosity=2)