# utils/entity_normalizer.py
# Resolves employee identity safely before DB operations
# Handles ambiguity, duplicates, and missing identifiers

from db.database import (
    get_employee_by_id,
    get_employee_by_name
)


def normalize_employee(data: dict):
    """
    Resolve employee from provided data.
    Priority:
    1. employee_id
    2. name
    """

    # -------------------------
    # Case 1: employee_id provided
    # -------------------------
    employee_id = data.get("employee_id")
    if employee_id:
        try:
            employee_id = int(employee_id)
        except ValueError:
            return {
                "status": "error",
                "message": "Employee ID must be a number."
            }

        employee = get_employee_by_id(employee_id)
        if not employee:
            return {
                "status": "error",
                "message": f"No employee found with ID {employee_id}."
            }

        return {
            "status": "resolved",
            "employee": employee
        }

    # -------------------------
    # Case 2: name provided
    # -------------------------
    name = data.get("name")
    if name:
        employees = get_employee_by_name(name)

        if not employees:
            return {
                "status": "error",
                "message": f"No employee found with name '{name}'."
            }

        if len(employees) == 1:
            return {
                "status": "resolved",
                "employee": employees[0]
            }

        # -------------------------
        # Ambiguous (multiple employees)
        # -------------------------
        return {
            "status": "ambiguous",
            "message": (
                f"There are {len(employees)} employees named '{name}'.\n"
                "Please specify one using employee ID, email, or department."
            ),
            "candidates": employees
        }

    # -------------------------
    # Nothing usable provided
    # -------------------------
    return {
        "status": "error",
        "message": "Please specify employee name or employee ID."
    }