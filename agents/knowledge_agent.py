# agents/knowledge_agent.py
# This file defines KnowledgeAgent.
# It answers HR-related questions using a simple text file.
# No AI logic and no vector DB library is used.
# This is a lightweight, beginner-friendly knowledge lookup.

from pathlib import Path


class KnowledgeAgent:
    """
    KnowledgeAgent handles:
    - Loading HR policy text from a file
    - Answering HR-related questions using simple keyword search
    """

    def __init__(self):
        """
        Load HR policy text when the agent is initialized.
        """
        policy_path = Path(__file__).parent.parent / "data" / "hr_policy.txt"

        if not policy_path.exists():
            self.policy_text = ""
        else:
            with open(policy_path, "r", encoding="utf-8") as file:
                self.policy_text = file.read()

    def search_policy(self, query):
        """
        Search HR policy text using simple keyword matching.

        Steps:
        1. Convert query to lowercase
        2. Split query into keywords
        3. Return lines that contain any keyword
        """

        if not self.policy_text:
            return {
                "status": "no_data",
                "message": "HR policy file not found or empty."
            }

        query = query.lower()
        keywords = query.split()

        matched_lines = []

        for line in self.policy_text.splitlines():
            line_lower = line.lower()
            for word in keywords:
                if word in line_lower:
                    matched_lines.append(line.strip())
                    break

        if not matched_lines:
            return {
                "status": "not_found",
                "message": "No relevant HR policy found for your query."
            }

        return {
            "status": "found",
            "results": matched_lines
        }