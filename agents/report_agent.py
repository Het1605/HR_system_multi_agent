# agents/report_agent.py
# Handles daily work report logic and PDF generation
# HR-driven attendance model

from datetime import datetime
from db.database import get_employee_by_id, get_working_hours
from utils.report_generator import generate_daily_report_pdf


class ReportAgent:
    def generate_daily_report(self, employee_id, date):
        """
        Generate a daily work report PDF for an employee
        using HR-assigned working hours.
        """

        # ---------- Fetch employee ----------
        employee = get_employee_by_id(employee_id)
        if not employee:
            return {
                "status": "error",
                "message": "Employee not found."
            }

        # ---------- Fetch working hours ----------
        working_hours_data = get_working_hours(employee_id, date)
        if not working_hours_data:
            return {
                "status": "error",
                "message": "No working hours assigned for this date."
            }

        start_time = working_hours_data["start_time"]
        end_time = working_hours_data["end_time"]

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