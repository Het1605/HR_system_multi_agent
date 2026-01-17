# agents/attendance_agent.py
# Read-only Attendance Agent (HR-driven model)

from db.database import get_working_hours


class AttendanceAgent:
    def get_attendance(self, employee_id, date):
        """
        Fetch working hours for an employee on a given date.
        Read-only access.
        """

        if not employee_id or not date:
            return None

        working_hours = get_working_hours(employee_id, date)

        if not working_hours:
            return None

        return {
            "employee_id": employee_id,
            "date": date,
            "start_time": working_hours["start_time"],
            "end_time": working_hours["end_time"]
        }