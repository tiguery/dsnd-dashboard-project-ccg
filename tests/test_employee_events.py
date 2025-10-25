# tests/test_employee_events.py
import sqlite3
from pathlib import Path
import pytest

# ---- pytest fixture: db_path ----
@pytest.fixture
def db_path() -> Path:
    # project_root/tests/.. -> project_root
    project_root = Path(__file__).resolve().parents[1]
    return project_root / "python-package" / "employee_events" / "employee_events.db"

def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None

def test_db_exists(db_path: Path):
    assert db_path.exists(), f"Database not found at {db_path}"

def test_employee_table_exists(db_path: Path):
    conn = sqlite3.connect(db_path)
    try:
        assert _table_exists(conn, "employee")
    finally:
        conn.close()

def test_team_table_exists(db_path: Path):
    conn = sqlite3.connect(db_path)
    try:
        assert _table_exists(conn, "team")
    finally:
        conn.close()

def test_employee_events_table_exists(db_path: Path):
    conn = sqlite3.connect(db_path)
    try:
        assert _table_exists(conn, "employee_events")
    finally:
        conn.close()
