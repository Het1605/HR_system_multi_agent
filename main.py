# main.py
# This file is the ENTRY POINT of the HR system.
# User interacts via terminal (CLI).
# This file:
# - Takes user input
# - Converts it into a structured intent (mock for now)
# - Sends intent to Orchestrator
# - Prints the response

from orchestrator import Orchestrator
from datetime import datetime


def mock_intent_parser(user_input):
    """
    TEMPORARY / MOCK intent parser.

    This simulates what an AI API (OpenRouter / Gemini) will do later.
    For now, we use simple keyword rules.

    Returns a structured intent dictionary.
    """

    text = user_input.lower()

    # ----------------------------
    # Employee registration
    # ----------------------------
    if "register" in text:
        return {
            "intent": "register_employee",
            "name": "Rahul",
            "email": "rahul@gmail.com",
            "department": "IT"
        }

    # ----------------------------
    # Find employee
    # ----------------------------
    if "find" in text:
        return {
            "intent": "find_employee",
            "name": "Rahul"
        }

    # ----------------------------
    # Start work
    # ----------------------------
    if "start work" in text:
        return {
            "intent": "start_work",
            "employee_id": 1,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "start_time": datetime.now().strftime("%H:%M")
        }

    # ----------------------------
    # End work
    # ----------------------------
    if "end work" in text:
        return {
            "intent": "end_work",
            "employee_id": 1,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "end_time": datetime.now().strftime("%H:%M")
        }

    # ----------------------------
    # Daily report
    # ----------------------------
    if "report" in text:
        return {
            "intent": "daily_report",
            "employee_id": 1,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

    # ----------------------------
    # HR policy
    # ----------------------------
    if "policy" in text:
        return {
            "intent": "hr_policy",
            "query": user_input
        }

    return {
        "intent": "unknown"
    }


def main():
    """
    Main terminal loop.
    """
    orchestrator = Orchestrator()

    print("🤖 HR Management System")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        intent_data = mock_intent_parser(user_input)
        response = orchestrator.handle_intent(intent_data)

        print("Bot:", response)
        print()


if __name__ == "__main__":
    main()