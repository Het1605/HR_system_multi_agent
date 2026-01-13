# agents/attendance_agent.py
# Read-only Attendance Agent

from db.database import get_attendance_for_date
from datetime import date as date_obj


class AttendanceAgent:
    def get_attendance(self, employee_id, date=None):
        """
        Fetch attendance record for an employee (read-only).
        """

        # Default to fixed date or today (as per your DB initialization)
        if not date:
            date = date_obj.today().isoformat()

        attendance = get_attendance_for_date(employee_id, date)

        if not attendance:
            return None

        return {
            "employee_id": employee_id,
            "date": date,
            "start_time": attendance.get("start_time"),
            "end_time": attendance.get("end_time")
        }