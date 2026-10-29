"""SQLite persistence and reusable validation helpers for Esports IQ."""
from __future__ import annotations
import json
import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any
import pandas as pd

DB_PATH = Path(os.environ.get("ESPORTS_IQ_DB_PATH", str(Path(__file__).resolve().parent / "esports_iq.db")))
REQUIRED_COLUMNS = ["shop_name", "product_name", "category", "units_sold", "unit_price", "stock_qty"]
NUMERIC_COLUMNS = ["units_sold", "unit_price", "stock_qty"]


@contextmanager
def connect(db_path: str | Path | None = None):
    path = Path(db_path) if db_path else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row

    try:
        conn.execute("PRAGMA journal_mode=WAL")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str | Path | None = None) -> None:
    with connect(db_path) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS dataset_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            created_at TEXT NOT NULL,
            row_count INTEGER NOT NULL,
            data_json TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            shop TEXT,
            action TEXT NOT NULL
        )""")


def validate_required_columns(raw: pd.DataFrame) -> list[str]:
    normalized = {str(c).strip().lower().replace("-", "_").replace(" ", "_") for c in raw.columns}
    # Alias matching is handled by the app before this helper is called.
    return [col for col in REQUIRED_COLUMNS if col not in normalized]


def validate_prepared_data(df: pd.DataFrame) -> list[str]:
    """Return validation errors for already-normalized/prepared business data."""
    errors: list[str] = []
    if df.empty:
        return ["The dataset has no valid rows after cleaning."]
    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing required numeric column: {col}")
            continue
        if df[col].isna().any():
            errors.append(f"Column '{col}' contains missing or non-numeric values.")
        if (df[col].dropna() < 0).any():
            errors.append(f"Column '{col}' cannot contain negative values.")
    if "date" in df.columns:
        parsed = pd.to_datetime(df["date"], errors="coerce")
        if parsed.notna().sum() == 0:
            errors.append("The date column has no valid dates; sales trend and forecasting require valid dates.")
    return errors


def save_dataset(df: pd.DataFrame, filename: str, db_path: str | Path | None = None) -> int:
    init_db(db_path)
    safe_df = df.copy()
    # Convert timestamps and missing values into JSON-safe values.
    safe_df = safe_df.astype(object).where(pd.notna(safe_df), None)
    records: list[dict[str, Any]] = json.loads(safe_df.to_json(orient="records", date_format="iso"))
    with connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO dataset_versions(filename, created_at, row_count, data_json) VALUES (?, ?, ?, ?)",
            (filename, datetime.now().isoformat(timespec="seconds"), len(df), json.dumps(records, ensure_ascii=False))
        )
        return int(cur.lastrowid)


def load_latest_dataset(db_path: str | Path | None = None) -> tuple[pd.DataFrame | None, dict[str, Any] | None]:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute("SELECT id, filename, created_at, row_count, data_json FROM dataset_versions ORDER BY id DESC LIMIT 1").fetchone()
    if row is None:
        return None, None
    return pd.DataFrame(json.loads(row["data_json"])), {
        "id": row["id"], "filename": row["filename"], "created_at": row["created_at"], "row_count": row["row_count"]
    }


def log_event(username: str, role: str, shop: str | None, action: str, db_path: str | Path | None = None) -> None:
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            "INSERT INTO audit_events(timestamp, username, role, shop, action) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().isoformat(timespec="seconds"), str(username), str(role), shop, str(action))
        )


def recent_audit_events(limit: int = 100, db_path: str | Path | None = None) -> pd.DataFrame:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute("SELECT timestamp, username, role, shop, action FROM audit_events ORDER BY id DESC LIMIT ?", (int(limit),)).fetchall()
    return pd.DataFrame([dict(row) for row in rows])
