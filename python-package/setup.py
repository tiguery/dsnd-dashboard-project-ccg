# python-package/setup.py
from setuptools import setup, find_packages

setup(
    name="employee_events",
    version="0.1.0",
    description="APIs for employee_events database access",
    packages=find_packages(),
    package_data={"employee_events": ["employee_events.db"]},
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.9",
)
