# python-package/employee_events/employee.py
from .query_base import Employee as _Employee
__all__ = ["Employee"]

class Employee(_Employee):
    """
    Intentionally inherits all behavior from QueryBase.Employee.
    Add employee-only methods here if needed later.
    """
    pass
