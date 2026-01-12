# agents/report_agent.py
# This file defines ReportAgent.
# It generates daily working hours reports for employees.
# No AI logic is used here.
# This agent ONLY reads data and calculates results.

from datetime import datetime
from db.database import get_attendance_for_date


class ReportAgent:
    """
    ReportAgent handles:
    - Generating daily working hours report for an employee
    """

    def generate_daily_report(self, employee_id, date):
        """
        Generate a daily work report for a given employee and date.

        Steps:
        1. Fetch attendance record
        2. Validate start and end time
        3. Calculate working hours
        4. Return structured report
        """

        attendance = get_attendance_for_date(employee_id, date)

        # Case 1: No attendance record
        if attendance is None:
            return {
                "status": "no_record",
                "message": "No attendance record found for this date."
            }

        start_time = attendance["start_time"]
        end_time = attendance["end_time"]

        # Case 2: Work not started
        if start_time is None:
            return {
                "status": "not_started",
                "message": "Work has not been started for this date."
            }

        # Case 3: Work not ended
        if end_time is None:
            return {
                "status": "in_progress",
                "message": "Work is still in progress. End time not recorded yet.",
                "start_time": start_time
            }

        # Case 4: Calculate working hours
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_dt = datetime.strptime(end_time, "%H:%M")

        duration = end_dt - start_dt
        total_minutes = int(duration.total_seconds() // 60)

        hours = total_minutes // 60
        minutes = total_minutes % 60

        return {
            "status": "completed",
            "employee_id": employee_id,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "working_hours": f"{hours}h {minutes}m"
        }