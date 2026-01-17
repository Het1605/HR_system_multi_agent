# orchestrator.py
# Supervisor agent with proper stateful conversation handling
# Handles multi-step flows for registration, attendance, and reports

from agents.employee_agent import EmployeeAgent
from agents.attendance_agent import AttendanceAgent
from agents.report_agent import ReportAgent
from agents.knowledge_agent import KnowledgeAgent

from db.database import (
    attendance_exists,
    assign_working_hours,
    get_working_hours
)

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
        intent = self.state["current_intent"]

        # ---------- REGISTRATION (special case) ----------
        if intent == "register_employee":
            values = [v.strip() for v in user_input.split(",") if v.strip()]
            required_fields = ["name", "email", "department"]

            missing_fields = [
                f for f in required_fields
                if not self.state["pending_data"].get(f)
            ]

            for i, value in enumerate(values):
                if i < len(missing_fields):
                    self.state["pending_data"][missing_fields[i]] = value

            return self._continue_register_employee()

        # ---------- ALL OTHER FLOWS (simple assignment) ----------
        field = self.state["expected_field"]
        self.state["pending_data"][field] = user_input.strip()

        if intent == "daily_report":
            return self._continue_daily_report()
        
        if intent == "attendance_info":
            self.state["pending_data"][self.state["expected_field"]] = user_input.strip()
            return self._continue_attendance_info()

        if intent == "find_employee":
            response = self.employee_agent.find_employee(
                name=self.state["pending_data"].get("name"),
                employee_id=self.state["pending_data"].get("employee_id")
            )
            self.reset_state()
            return response
        
        if intent == "assign_working_hours":
            self.state["pending_data"][self.state["expected_field"]] = user_input.strip()
            return self._continue_assign_working_hours()
        
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
    # Daily report flow
    # -------------------------
    def _continue_daily_report(self):
        if not self.state["pending_data"].get("employee_id"):
            self.state["expected_field"] = "employee_id"
            return "Please provide your employee ID to generate daily report."

        response = self.report_agent.generate_daily_report(
            employee_id=self.state["pending_data"]["employee_id"],
            date=self.state["pending_data"].get("date")
        )

        # Reset state after terminal response
        self.reset_state()

        # Human-friendly response
        if response.get("status") == "success":
            return (
                "📄 Your daily work report has been generated successfully.\n"
                f"File saved at: {response['file_path']}"
            )

        return response.get("message", "Unable to generate daily report.")
    
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
    # Attendance info flow (READ ONLY)
    # -------------------------
    def _continue_attendance_info(self):
        if not self.state["pending_data"].get("employee_id"):
            self.state["expected_field"] = "employee_id"
            return "Please provide employee ID to check working hours."

        if not self.state["pending_data"].get("date"):
            self.state["expected_field"] = "date"
            return "Please provide the date."

        employee_id = self.state["pending_data"]["employee_id"]
        date = self.state["pending_data"]["date"]

        attendance = self.attendance_agent.get_attendance(
            employee_id=employee_id,
            date=date
        )

        self.reset_state()

        if not attendance:
            return (
                f"No working hours assigned for employee {employee_id} on {date}."
            )

        start_time = attendance["start_time"]
        end_time = attendance["end_time"]

        return (
            f"🕘 Working Hours for Employee ID {employee_id}\n"
            f"📅 Date: {date}\n"
            f"⏰ Start Time: {start_time}\n"
            f"⏰ End Time: {end_time}"
        )

    # -------------------------
    # Assign working hours flow (HR-driven)
    # -------------------------
    def _continue_assign_working_hours(self):
        required_fields = ["employee_id", "date", "start_time", "end_time"]

        missing_fields = [
            f for f in required_fields
            if not self.state["pending_data"].get(f)
        ]

        # Ask for missing info
        if missing_fields:
            self.state["expected_field"] = missing_fields[0]

            missing_text = "\n".join(f"- {f}" for f in missing_fields)
            return (
                "To assign working hours, please provide:\n"
                f"{missing_text}"
            )

        employee_id = self.state["pending_data"]["employee_id"]
        date = self.state["pending_data"]["date"]
        start_time = self.state["pending_data"]["start_time"]
        end_time = self.state["pending_data"]["end_time"]

        # Check duplicate
        if attendance_exists(employee_id, date):
            self.reset_state()
            return (
                f"⚠️ Working hours already exist for employee {employee_id} on {date}."
            )

        # Assign working hours
        assign_working_hours(
            employee_id=employee_id,
            date=date,
            start_time=start_time,
            end_time=end_time
        )

        self.reset_state()

        return (
            f"✅ Working hours assigned successfully.\n"
            f"Employee ID: {employee_id}\n"
            f"Date: {date}\n"
            f"Time: {start_time} – {end_time}"
        )

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
                "- Attendance information\n"
                "- Daily work reports\n"
                "- HR policies\n\n"
                "How can I help you?"
            )
        
        if intent == "help":
            return (
                "📋 Here’s what I can help you with:\n"
                "1️⃣ Register employees\n"
                "2️⃣ Find employee details\n"
                "3️⃣ View attendance & working hours\n"
                "4️⃣ Generate daily work reports\n"
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
        
        # -------- ATTENDANCE INFO (READ ONLY) --------
        if intent == "attendance_info":
            self.state["current_intent"] = "attendance_info"
            self.state["pending_data"].update(
                {k: v for k, v in intent_data.items() if v}
            )
            return self._continue_attendance_info()

        
        # -------- FIND EMPLOYEE (FIXED) --------
        if intent == "find_employee":
            self.state["current_intent"] = "find_employee"
            self.state["pending_data"].update(
                {k: v for k, v in intent_data.items() if v}
            )

            # If neither ID nor name provided, ask for it
            if not self.state["pending_data"].get("employee_id") and not self.state["pending_data"].get("name"):
                self.state["expected_field"] = "employee_id"
                return "Please provide employee_id or name."

            # We already have enough data → search
            response = self.employee_agent.find_employee(
                name=self.state["pending_data"].get("name"),
                employee_id=self.state["pending_data"].get("employee_id")
            )

            self.reset_state()
            return response
        

        # -------- DAILY REPORT --------
        if intent == "daily_report":
            self.state["current_intent"] = "daily_report"
            self.state["pending_data"].update(
                {k: v for k, v in intent_data.items() if v}
            )
            return self._continue_daily_report()
        
        # -------- ASSIGN WORKING HOURS (HR) --------
        if intent == "assign_working_hours":
            self.state["current_intent"] = "assign_working_hours"
            self.state["pending_data"].update(
                {k: v for k, v in intent_data.items() if v}
            )
            return self._continue_assign_working_hours()

        # -------- HR POLICY --------
        
        if intent == "hr_policy":
            query = intent_data.get("query")

            if not query:
                return (
                    "📘 Please specify which HR policy you want to know about.\n"
                    "For example: leave policy, attendance policy, working hours."
                )

            response = self.knowledge_agent.search_policy(query)

            if not response:
                return (
                    "📘 I couldn’t find a matching HR policy.\n"
                    "You can ask about leave policy, attendance policy, or working hours."
                )

            return response

        return "Sorry, I cannot handle this request."
    
        