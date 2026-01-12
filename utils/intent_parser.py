# utils/intent_parser.py
# Converts raw user text into a SAFE, STRUCTURED intent
# Uses local Ollama with retries + guardrails

import json
from datetime import datetime
from utils.ai_client import call_ollama


# --------------------------------------------------
# Intent schema (single source of truth)
# --------------------------------------------------

INTENT_SCHEMA = {
    "intent": None,
    "employee_id": None,
    "name": None,
    "email": None,
    "department": None,
    "date": None,
    "start_time": None,
    "end_time": None,
    "query": None
}


# --------------------------------------------------
# Prompts
# --------------------------------------------------

BASE_SYSTEM_PROMPT = """
Extract intent and entities from the user message.
Return ONLY valid JSON.
Do NOT explain anything.
If unsure, still try.

Schema:
{
  "intent": null,
  "employee_id": null,
  "name": null,
  "email": null,
  "department": null,
  "date": null,
  "start_time": null,
  "end_time": null,
  "query": null
}

Valid intents:
register_employee
find_employee
start_work
end_work
daily_report
hr_policy
"""


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def _today_date():
    return datetime.now().strftime("%Y-%m-%d")


def _current_time():
    return datetime.now().strftime("%H:%M")


def _fallback_intent():
    return {**INTENT_SCHEMA, "intent": "unknown"}


def _extract_json(text):
    """
    Extract JSON object from text (handles extra words).
    """
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON found")

    return text[start:end + 1]


def _rule_based_intent_hint(user_input):
    """
    Light rule-based hints to help local LLM.
    """
    text = user_input.lower()

    if "register" in text and "employee" in text:
        return "register_employee"
    if "start work" in text:
        return "start_work"
    if "end work" in text:
        return "end_work"
    if "report" in text:
        return "daily_report"
    if "policy" in text:
        return "hr_policy"

    return None


# --------------------------------------------------
# Main function
# --------------------------------------------------

def parse_intent(user_input):
    """
    Convert user input text into structured intent.
    Includes:
    - rule hints
    - AI retry
    - JSON extraction
    - safe fallback
    """

    hint = _rule_based_intent_hint(user_input)

    system_prompt = BASE_SYSTEM_PROMPT
    if hint:
        system_prompt += f"\nHint: intent is likely '{hint}'."

    # ---------- TRY 1 ----------
    try:
        raw = call_ollama(system_prompt, user_input)
        clean = _extract_json(raw)
        parsed = json.loads(clean)

    # ---------- RETRY ----------
    except Exception:
        try:
            raw = call_ollama(BASE_SYSTEM_PROMPT, user_input)
            clean = _extract_json(raw)
            parsed = json.loads(clean)
        except Exception as e:
            print("⚠️ AI intent parsing failed:", e)
            return _fallback_intent()

    # ---------- Merge with schema ----------
    intent_data = {**INTENT_SCHEMA, **parsed}

    # ---------- Normalize date & time ----------
    if intent_data["date"] in ("today", None):
        intent_data["date"] = _today_date()

    if intent_data["intent"] == "start_work" and intent_data["start_time"] is None:
        intent_data["start_time"] = _current_time()

    if intent_data["intent"] == "end_work" and intent_data["end_time"] is None:
        intent_data["end_time"] = _current_time()

    return intent_data