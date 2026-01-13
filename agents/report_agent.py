# agents/report_agent.py
# Handles daily work report logic and PDF generation

from datetime import date as date_obj, datetime
from db.database import get_employee_by_id, get_attendance_for_date
from utils.report_generator import generate_daily_report_pdf


class ReportAgent:
    def generate_daily_report(self, employee_id, date=None):
        """
        Generate a daily work report PDF for an employee.
        """

        # Use today's date if not provided
        if not date:
            date = date_obj.today().isoformat()

        # ---------- Fetch employee ----------
        employee = get_employee_by_id(employee_id)
        if not employee:
            return {
                "status": "error",
                "message": "Employee not found."
            }

        # ---------- Fetch attendance ----------
        attendance = get_attendance_for_date(employee_id, date)
        if not attendance:
            return {
                "status": "error",
                "message": "No attendance record found for this date."
            }

        start_time = attendance.get("start_time")
        end_time = attendance.get("end_time")

        if not start_time:
            return {
                "status": "error",
                "message": "Work has not been started yet."
            }

        if not end_time:
            return {
                "status": "error",
                "message": "Work has not been ended yet."
            }

        # ---------- Calculate working hours ----------
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_dt = datetime.strptime(end_time, "%H:%M")

        working_seconds = (end_dt - start_dt).seconds
        working_hours = round(working_seconds / 3600, 2)

        # ---------- Prepare report data ----------
        report_data = {
            "employee_id": employee["employee_id"],
            "name": employee["name"],
            "email": employee["email"],
            "department": employee["department"],
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "working_hours": working_hours
        }

        # ---------- Generate PDF ----------
        file_path = generate_daily_report_pdf(report_data)

        return {
            "status": "success",
            "message": "Daily work report generated successfully.",
            "file_path": file_path
        }