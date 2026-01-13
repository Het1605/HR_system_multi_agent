# agents/employee_agent.py
# This file defines EmployeeAgent.
# It handles employee registration and employee search.
# It does NOT contain any AI logic.
# It uses database.py for all DB operations.

from db.database import (
    add_employee,
    employee_exists,
    get_employee_by_id,
    get_employee_by_name
)


class EmployeeAgent:
    """
    EmployeeAgent handles:
    - Employee registration
    - Finding employees
    """

    def register_employee(self, name, email, department):
        """
        Register a new employee.

        Steps:
        1. Check if employee already exists using email
        2. If exists, return message
        3. If not, add employee to DB
        """

        if employee_exists(email):
            return {
                "status": "exists",
                "message": "Employee already registered with this email."
            }
        department = department.strip().upper()
        
        employee_id = add_employee(name, email, department)

        return {
            "status": "success",
            "message": "Employee registered successfully.",
            "employee_id": employee_id
        }

    def find_employee(self, employee_id=None, name=None):
        """
        Find employee by ID or by name.

        Rules:
        - If employee_id is provided, search by ID
        - If name is provided, search by name
        - If multiple employees found with same name, return list
        """

        # Case 1: Search by employee ID
        if employee_id is not None:
            employee = get_employee_by_id(employee_id)

            if employee:
                return {
                    "status": "found",
                    "employee": employee
                }

            return {
                "status": "not_found",
                "message": "Employee not found with given ID."
            }

        # Case 2: Search by name
        if name is not None:
            employees = get_employee_by_name(name)

            if not employees:
                return {
                    "status": "not_found",
                    "message": "No employee found with this name."
                }

            # Multiple employees with same name
            if len(employees) > 1:
                return {
                    "status": "multiple_found",
                    "message": "Multiple employees found with this name.",
                    "employees": employees
                }

            # Only one employee found
            return {
                "status": "found",
                "employee": employees[0]
            }

        return {
            "status": "error",
            "message": "Please provide employee_id or name."
        }