# orchestrator.py
# This file defines the Supervisor / Orchestrator.
# It receives structured intent and decides which agent to call.
# It does NOT contain business logic or DB logic.
# Think of this as the "brain" that coordinates agents.

from agents.employee_agent import EmployeeAgent
from agents.attendance_agent import AttendanceAgent
from agents.report_agent import ReportAgent
from agents.knowledge_agent import KnowledgeAgent


class Orchestrator:
    """
    Orchestrator coordinates between multiple agents.
    It decides WHICH agent should handle the request.
    """

    def __init__(self):
        self.employee_agent = EmployeeAgent()
        self.attendance_agent = AttendanceAgent()
        self.report_agent = ReportAgent()
        self.knowledge_agent = KnowledgeAgent()

    def handle_intent(self, intent_data):
        """
        Main entry point for handling structured intent.

        intent_data example:
        {
            "intent": "register_employee",
            "name": "Rahul",
            "email": "rahul@gmail.com",
            "department": "IT"
        }
        """

        intent = intent_data.get("intent")

        # -------------------------------
        # Employee-related intents
        # -------------------------------
        if intent == "register_employee":
            return self.employee_agent.register_employee(
                name=intent_data.get("name"),
                email=intent_data.get("email"),
                department=intent_data.get("department")
            )

        if intent == "find_employee":
            return self.employee_agent.find_employee(
                employee_id=intent_data.get("employee_id"),
                name=intent_data.get("name")
            )

        # -------------------------------
        # Attendance-related intents
        # -------------------------------
        if intent == "start_work":
            return self.attendance_agent.start_work(
                employee_id=intent_data.get("employee_id"),
                date=intent_data.get("date"),
                start_time=intent_data.get("start_time")
            )

        if intent == "end_work":
            return self.attendance_agent.end_work(
                employee_id=intent_data.get("employee_id"),
                date=intent_data.get("date"),
                end_time=intent_data.get("end_time")
            )

        # -------------------------------
        # Report-related intents
        # -------------------------------
        if intent == "daily_report":
            return self.report_agent.generate_daily_report(
                employee_id=intent_data.get("employee_id"),
                date=intent_data.get("date")
            )

        # -------------------------------
        # Knowledge-related intents
        # -------------------------------
        if intent == "hr_policy":
            return self.knowledge_agent.search_policy(
                query=intent_data.get("query")
            )

        # -------------------------------
        # Unknown intent
        # -------------------------------
        return {
            "status": "error",
            "message": "Unknown intent."
        }