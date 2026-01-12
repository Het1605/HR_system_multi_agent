# agents/attendance_agent.py
# This file defines AttendanceAgent.
# It handles employee start and end time for a specific date.
# No AI logic is used here.
# All DB operations are done via database.py.

from db.database import (
    get_attendance_for_date,
    add_start_time,
    add_end_time
)


class AttendanceAgent:
    """
    AttendanceAgent handles:
    - Starting work for an employee
    - Ending work for an employee
    Attendance is always date-specific.
    """

    def start_work(self, employee_id, date, start_time):
        """
        Record start time for an employee on a given date.

        Rules:
        - Employee must not have already started work for the date
        - Start time cannot be overwritten
        """

        attendance = get_attendance_for_date(employee_id, date)

        # Case 1: Attendance already exists and start_time is recorded
        if attendance and attendance["start_time"] is not None:
            return {
                "status": "already_started",
                "message": "Work has already been started for today.",
                "start_time": attendance["start_time"]
            }

        # Case 2: No attendance record exists → create start time
        add_start_time(employee_id, date, start_time)

        return {
            "status": "started",
            "message": "Work start time recorded successfully.",
            "start_time": start_time
        }

    def end_work(self, employee_id, date, end_time):
        """
        Record end time for an employee on a given date.

        Rules:
        - Work must be started before ending
        - End time cannot be overwritten
        """

        attendance = get_attendance_for_date(employee_id, date)

        # Case 1: No attendance record at all
        if attendance is None or attendance["start_time"] is None:
            return {
                "status": "not_started",
                "message": "Cannot end work. Work has not been started yet."
            }

        # Case 2: End time already recorded
        if attendance["end_time"] is not None:
            return {
                "status": "already_ended",
                "message": "Work has already been ended for today.",
                "end_time": attendance["end_time"]
            }

        # Case 3: Valid end work
        add_end_time(employee_id, date, end_time)

        return {
            "status": "ended",
            "message": "Work end time recorded successfully.",
            "end_time": end_time
        }