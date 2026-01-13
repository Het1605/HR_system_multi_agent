# orchestrator.py
# Supervisor agent with proper stateful conversation handling
# Handles multi-step flows for registration, attendance, and reports

from agents.employee_agent import EmployeeAgent
from agents.attendance_agent import AttendanceAgent
from agents.report_agent import ReportAgent
from agents.knowledge_agent import KnowledgeAgent


class Orchestrator:
    def __init__(self):
        self.employee_agent = EmployeeAgent()
        self.attendance_agent = AttendanceAgent()
        self.report_agent = ReportAgent()
        self.knowledge_agent = KnowledgeAgent()

        # Conversation state
        self.state = {
            "current_intent": None,
            "pending_data": {},
            "expected_field": None
        }

    # -------------------------
    # State helpers
    # -------------------------
    def has_active_state(self):
        return self.state["current_intent"] is not None

    def reset_state(self):
        self.state = {
            "current_intent": None,
            "pending_data": {},
            "expected_field": None
        }

    # -------------------------
    # Follow-up handler
    # -------------------------
    def handle_followup(self, user_input):
        field = self.state["expected_field"]
        intent = self.state["current_intent"]

        
        # Support comma-separated multiple values
        values = [v.strip() for v in user_input.split(",") if v.strip()]

        intent = self.state["current_intent"]

        if intent == "register_employee":
            required_fields = ["name", "email", "department"]

            # Find which fields are still missing
            missing_fields = [
                f for f in required_fields
                if not self.state["pending_data"].get(f)
            ]

            # Map provided values to missing fields (in order)
            for i, value in enumerate(values):
                if i < len(missing_fields):
                    self.state["pending_data"][missing_fields[i]] = value

            return self._continue_register_employee()

        if intent == "register_employee":
            return self._continue_register_employee()

        if intent == "start_work":
            return self._continue_start_work()

        if intent == "end_work":
            return self._continue_end_work()

        if intent == "daily_report":
            return self._continue_daily_report()
        
        if intent == "check_attendance_summary":
            return self._continue_attendance_summary()


        return "Something went wrong."

    # -------------------------
    # Register employee flow
    # -------------------------
    def _continue_register_employee(self):
        required_fields = ["name", "email", "department"]

        missing_fields = [
            field for field in required_fields
            if not self.state["pending_data"].get(field)
        ]

        # If something is missing, ask clearly
        if missing_fields:
            # Always expect the NEXT missing field
            self.state["expected_field"] = missing_fields[0]

            missing_text = "\n".join(f"- {field}" for field in missing_fields)

            return (
                "To register an employee, please provide the following details:\n"
                f"{missing_text}"
            )

        # All data present → register
        response = self.employee_agent.register_employee(
            name=self.state["pending_data"]["name"],
            email=self.state["pending_data"]["email"],
            department=self.state["pending_data"]["department"]
        )

        self.reset_state()
        return response
    # -------------------------
    # Start work flow
    # -------------------------
    def _continue_start_work(self):
        if not self.state["pending_data"].get("employee_id"):
            self.state["expected_field"] = "employee_id"
            return "Please provide employee ID."

        response = self.attendance_agent.start_work(
            employee_id=self.state["pending_data"]["employee_id"],
            date=self.state["pending_data"].get("date"),
            start_time=self.state["pending_data"].get("start_time")
        )

        self.reset_state()
        return response

    # -------------------------
    # End work flow
    # -------------------------
    def _continue_end_work(self):
        if not self.state["pending_data"].get("employee_id"):
            self.state["expected_field"] = "employee_id"
            return "Please provide employee ID."

        response = self.attendance_agent.end_work(
            employee_id=self.state["pending_data"]["employee_id"],
            date=self.state["pending_data"].get("date"),
            end_time=self.state["pending_data"].get("end_time")
        )

        self.reset_state()
        return response

    # -------------------------
    # Daily report flow
    # -------------------------
    def _continue_daily_report(self):
        if not self.state["pending_data"].get("employee_id"):
            self.state["expected_field"] = "employee_id"
            return "Please provide employee ID."

        response = self.report_agent.generate_daily_report(
            employee_id=self.state["pending_data"]["employee_id"],
            date=self.state["pending_data"].get("date")
        )

        self.reset_state()
        return response
    
    def _continue_attendance_summary(self):
        if not self.state["pending_data"].get("employee_id"):
            self.state["expected_field"] = "employee_id"
            return "Please provide employee ID."

        employee_id = self.state["pending_data"]["employee_id"]
        date = self.state["pending_data"].get("date")

        attendance = self.attendance_agent.get_attendance(
            employee_id=employee_id,
            date=date
        )

        report = self.report_agent.generate_daily_report(
            employee_id=employee_id,
            date=date
        )

        self.reset_state()

        return {
            "status": "success",
            "attendance": attendance,
            "report": report
        }

    # -------------------------
    # Main intent handler
    # -------------------------
    def handle_intent(self, intent_data):
        intent = intent_data.get("intent")

        if intent == "greeting":
            return (
                "👋 Hi! I’m your HR assistant.\n"
                "I can help you with:\n"
                "- Employee registration\n"
                "- Attendance (start/end work)\n"
                "- Daily work reports\n"
                "- HR policies\n\n"
                "How can I help you?"
            )
        
        if intent == "help":
            return (
                "📋 Here’s what I can help you with:\n"
                "1️⃣ Register employees\n"
                "2️⃣ Find employee details\n"
                "3️⃣ Start / end work (attendance)\n"
                "4️⃣ View daily working hours\n"
                "5️⃣ HR policies\n\n"
                "Just tell me what you want to do 😊"
            )

        # -------- REGISTER EMPLOYEE --------
        if intent == "register_employee":
            self.state["current_intent"] = "register_employee"
            self.state["pending_data"].update(
                {k: v for k, v in intent_data.items() if v}
            )
            return self._continue_register_employee()

        # -------- FIND EMPLOYEE --------
        if intent == "find_employee":
            return self.employee_agent.find_employee(
                name=intent_data.get("name"),
                employee_id=intent_data.get("employee_id")
            )

        # -------- START WORK --------
        if intent == "start_work":
            self.state["current_intent"] = "start_work"
            self.state["pending_data"].update(
                {k: v for k, v in intent_data.items() if v}
            )
            return self._continue_start_work()

        # -------- END WORK --------
        if intent == "end_work":
            self.state["current_intent"] = "end_work"
            self.state["pending_data"].update(
                {k: v for k, v in intent_data.items() if v}
            )
            return self._continue_end_work()
        
        if intent == "check_attendance_summary":
            self.state["current_intent"] = "check_attendance_summary"
            self.state["pending_data"].update(
                {k: v for k, v in intent_data.items() if v}
            )
            return self._continue_attendance_summary()

        # -------- DAILY REPORT --------
        if intent == "daily_report":
            self.state["current_intent"] = "daily_report"
            self.state["pending_data"].update(
                {k: v for k, v in intent_data.items() if v}
            )
            return self._continue_daily_report()

        # -------- HR POLICY --------
        if intent == "hr_policy":
            return self.knowledge_agent.search_policy(
                intent_data.get("query")
            )

        return "Sorry, I cannot handle this request."
    
        