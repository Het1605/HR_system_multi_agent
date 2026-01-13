# agents/knowledge_agent.py
# Read-only HR policy knowledge agent (FINAL FIX)

import os


class KnowledgeAgent:
    def __init__(self):
        self.policy_file = "data/hr_policy.txt"

        if not os.path.exists(self.policy_file):
            raise FileNotFoundError("HR policy file not found.")

        with open(self.policy_file, "r", encoding="utf-8") as f:
            self.policy_text = f.read()

        self.policies = self._parse_policies()

    def _parse_policies(self):
        """
        Parse policy file into a dict:
        {
          "leave policy": "LEAVE POLICY\n....",
          "attendance policy": "ATTENDANCE POLICY\n....",
        }
        """
        sections = self.policy_text.strip().split("\n\n")
        policy_map = {}

        for section in sections:
            lines = section.strip().split("\n")
            header = lines[0].strip().lower()
            policy_map[header] = section.strip()

        return policy_map

    def search_policy(self, query):
        """
        Return exact policy, all policies, or None.
        """
        if not query:
            return None

        q = query.lower().strip()

        # ---------- LIST ALL POLICIES ----------
        if any(k in q for k in ["hr policies", "all policies", "company policies"]):
            policy_list = "\n".join(
                f"- {title.upper()}"
                for title in self.policies.keys()
            )
            return (
                "📘 HR POLICIES AVAILABLE:\n"
                f"{policy_list}\n\n"
                "Ask me about any specific policy."
            )

        # ---------- EXACT MATCH ----------
        for header, content in self.policies.items():
            if header in q:
                return f"📘 {content}"

        return None