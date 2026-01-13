# from agents.employee_agent import EmployeeAgent

# agent = EmployeeAgent()

# print(agent.register_employee("Rahul", "rahul@gmail.com", "IT"))
# print(agent.find_employee(name="Rahul"))

# from agents.attendance_agent import AttendanceAgent

# agent = AttendanceAgent()

# print(agent.start_work(employee_id=1, date="2026-01-12", start_time="09:10"))
# print(agent.end_work(employee_id=1, date="2026-01-12", end_time="17:40"))


# from agents.report_agent import ReportAgent

# agent = ReportAgent()

# print(agent.generate_daily_report(employee_id=1, date="2026-01-12"))

# from agents.knowledge_agent import KnowledgeAgent

# agent = KnowledgeAgent()

# print(agent.search_policy("leave policy"))

# from orchestrator import Orchestrator

# orch = Orchestrator()

# print(orch.handle_intent({
#     "intent": "find_employee",
#     "name": "Rahul"
# }))

# from utils.ai_client import call_ollama

# system_prompt = """
# Convert user message into JSON.
# Return only JSON.
# """

# user_prompt = "Show my working hours today"

# print(call_ollama(system_prompt, user_prompt))


from utils.vector_store import VectorStore

vs = VectorStore("data/hr_policy.txt")
vs.load()

print(vs.search("leave policy"))
print(vs.search("attendance rules"))
print(vs.search("office timing"))