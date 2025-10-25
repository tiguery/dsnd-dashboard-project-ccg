# python-package/employee_events/query_base.py
from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from .sql_execution import SqlExecutorMixin

Row = Dict[str, Any]

class QueryBase(SqlExecutorMixin):
    """
    Shared queries usable for both Employee and Team.
    """

    # Productivity time series (positive/negative by date)
    def productivity_by_employee(self, employee_id: int) -> List[Row]:
        sql = """
        SELECT event_date,
               positive_events,
               negative_events
        FROM employee_events
        WHERE employee_id = ?
        ORDER BY event_date ASC
        """
        return self.execute(sql, (employee_id,))

    def productivity_by_team(self, team_id: int) -> List[Row]:
        sql = """
        SELECT event_date,
               SUM(positive_events) AS positive_events,
               SUM(negative_events) AS negative_events
        FROM employee_events
        WHERE team_id = ?
        GROUP BY event_date
        ORDER BY event_date ASC
        """
        return self.execute(sql, (team_id,))

    # Simple summaries
    def employee_summary(self, employee_id: int) -> List[Row]:
        sql = """
        SELECT
            e.employee_id,
            e.first_name || ' ' || e.last_name AS employee_name,
            t.team_name,
            COALESCE(SUM(ev.positive_events),0) AS total_positive,
            COALESCE(SUM(ev.negative_events),0) AS total_negative
        FROM employee e
        JOIN team t ON t.team_id = e.team_id
        LEFT JOIN employee_events ev ON ev.employee_id = e.employee_id
        WHERE e.employee_id = ?
        GROUP BY e.employee_id
        """
        return self.execute(sql, (employee_id,))

    def team_summary(self, team_id: int) -> List[Row]:
        sql = """
        SELECT
            t.team_id,
            t.team_name,
            t.shift,
            t.manager_name,
            COALESCE(SUM(ev.positive_events),0) AS total_positive,
            COALESCE(SUM(ev.negative_events),0) AS total_negative,
            COUNT(DISTINCT e.employee_id) AS headcount
        FROM team t
        LEFT JOIN employee e ON e.team_id = t.team_id
        LEFT JOIN employee_events ev ON ev.team_id = t.team_id
        WHERE t.team_id = ?
        GROUP BY t.team_id
        """
        return self.execute(sql, (team_id,))

    # Roster / names
    def team_members(self, team_id: int) -> List[Row]:
        sql = """
        SELECT e.employee_id,
               e.first_name || ' ' || e.last_name AS employee_name
        FROM employee e
        WHERE e.team_id = ?
        ORDER BY employee_name
        """
        return self.execute(sql, (team_id,))

    # Notes for either employee or team
    def employee_notes(self, employee_id: int) -> List[Row]:
        sql = """
        SELECT note_date, note
        FROM notes
        WHERE employee_id = ?
        ORDER BY note_date DESC
        """
        return self.execute(sql, (employee_id,))

    def team_notes(self, team_id: int) -> List[Row]:
        sql = """
        SELECT note_date, note
        FROM notes
        WHERE team_id = ?
        ORDER BY note_date DESC
        """
        return self.execute(sql, (team_id,))


class Employee(QueryBase):
    """
    Employee-scoped accessors
    """

    def profile(self, employee_id: int) -> Row:
        rows = self.employee_summary(employee_id)
        return rows[0] if rows else {}

    def timeseries(self, employee_id: int) -> List[Row]:
        return self.productivity_by_employee(employee_id)

    def notes(self, employee_id: int) -> List[Row]:
        return self.employee_notes(employee_id)


class Team(QueryBase):
    """
    Team-scoped accessors
    """

    def profile(self, team_id: int) -> Row:
        rows = self.team_summary(team_id)
        return rows[0] if rows else {}

    def timeseries(self, team_id: int) -> List[Row]:
        return self.productivity_by_team(team_id)

    def roster(self, team_id: int) -> List[Row]:
        return self.team_members(team_id)

    def notes(self, team_id: int) -> List[Row]:
        return self.team_notes(team_id)
