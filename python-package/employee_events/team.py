# python-package/employee_events/team.py
from .query_base import Team as _Team
__all__ = ["Team"]

class Team(_Team):
    """
    Intentionally inherits all behavior from QueryBase.Team.
    Add team-only methods here if needed later.
    """
    pass
