# main.py
# Entry point with state-aware input routing

from orchestrator import Orchestrator
from utils.intent_parser import parse_intent


def main():
    orchestrator = Orchestrator()

    print("🤖 HR Management System")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        # 🔑 KEY FIX: Check for active state
        if orchestrator.has_active_state():
            response = orchestrator.handle_followup(user_input)
        else:
            intent_data = parse_intent(user_input)

            if intent_data.get("intent") == "unknown":
                print("Bot: Sorry, I couldn’t understand that. Please rephrase.\n")
                continue

            response = orchestrator.handle_intent(intent_data)

        print("Bot:", response)
        print()


if __name__ == "__main__":
    main()