# python-package/employee_events/sql_execution.py
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence, Union, Dict, List

RowMapping = Dict[str, Any]

class SqlExecutorMixin:
    """
    Mixin to handle open/execute/close for SQLite queries.
    Usage:
        class MyQueries(SqlExecutorMixin): ...
        rows = self.execute("SELECT * FROM employee WHERE employee_id=?", (emp_id,))
    """

    def get_db_path(self) -> Path:
        # DB lives alongside this file in the package directory
        here = Path(__file__).resolve().parent
        return here / "employee_events.db"

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.get_db_path())
        conn.row_factory = sqlite3.Row
        return conn

    def execute(
        self,
        sql: str,
        params: Optional[Sequence[Any]] = None
    ) -> List[RowMapping]:
        params = params or ()
        conn = self._connect()
        try:
            cur = conn.execute(sql, params)
            rows = [dict(r) for r in cur.fetchall()]
            return rows
        finally:
            conn.close()
