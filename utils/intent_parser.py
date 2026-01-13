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
  "query": null
}

Valid intents:
register_employee
find_employee
attendance_info
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
    Priority matters.
    """
    text = user_input.lower().strip()

    # ---------- GREETING ----------
    if text in ["hi", "hello", "hey", "hii"]:
        return "greeting"

    # ---------- HELP / SERVICES ----------
    if any(k in text for k in ["service", "help", "what can you do"]):
        return "help"

    # ---------- REGISTER EMPLOYEE ----------
    if "register" in text and "employee" in text:
        return "register_employee"
    
    # ---------- HR POLICY ----------
    if "policy" in text:
        return "hr_policy"

    # ---------- ATTENDANCE INFO  ----------
    if any(k in text for k in [
        "attendance record",
        "attendance",
        "working hour",
        "working hours",
        "work hours"
    ]):
        return "attendance_info"

    # ---------- DAILY REPORT ----------
    if any(k in text for k in [
        "daily report",
        "work report",
        "generate report",
        "show report"
    ]):
        return "daily_report"

    

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

    # ---------- Normalize date ----------
    if intent_data["date"] in ("today", None):
        intent_data["date"] = _today_date()

    # ---------- FINAL INTENT OVERRIDE (CRITICAL FIX) ----------
    if hint == "attendance_info":
        intent_data["intent"] = "attendance_info"
    elif hint and not intent_data.get("intent"):
        intent_data["intent"] = hint

    # ---------- Ensure query for HR policy ----------
    if intent_data["intent"] == "hr_policy" and not intent_data.get("query"):
        intent_data["query"] = user_input

    return intent_data