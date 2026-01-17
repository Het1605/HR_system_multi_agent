# agents/knowledge_agent.py
# Knowledge agent using Vector DB (FAISS) for HR policies
# Handles:
# - All HR policies
# - Specific HR policy search
# - Proper formatting (NO broken titles like "CODE OF")

from utils.vector_store import VectorStore


class KnowledgeAgent:
    def __init__(self):
        """
        Initialize vector store and load HR policies.
        """
        self.vector_store = VectorStore("data/hr_policy.txt")
        self.vector_store.load()

    # --------------------------------------------------
    # Internal helper (CRITICAL FIX)
    # --------------------------------------------------
    def _split_policy(self, policy_text: str):
        """
        Split policy text into TITLE and BODY safely.

        Examples:
        - "LEAVE POLICY Employees are entitled..."
        - "CODE OF CONDUCT Employees must behave..."
        """

        policy_text = policy_text.strip()

        # Special case: CODE OF CONDUCT (3-word title)
        if policy_text.startswith("CODE OF CONDUCT"):
            title = "CODE OF CONDUCT"
            body = policy_text[len(title):].strip()
            return title, body

        # Default case: first two words are title
        parts = policy_text.split(" ", 2)

        if len(parts) < 3:
            # Fallback (should not happen, but safe)
            return policy_text, ""

        title = f"{parts[0]} {parts[1]}"
        body = parts[2].strip()

        return title, body

    # --------------------------------------------------
    # Public search API
    # --------------------------------------------------
    def search_policy(self, query: str):
        """
        Search HR policies.

        Behavior:
        - If user asks generally → return ALL policies
        - If user asks specifically → return best matched policy
        """

        if not query:
            return None

        q = query.lower()

        # ---------- CASE 1: User wants ALL HR policies ----------
        if any(k in q for k in [
            "hr policies",
            "all hr policies",
            "company policies",
            "tell me about hr policies",
            "list hr policies",
            "policies",
            "policy",
            "list out all policies"
            
        ]):
            policies = self.vector_store.get_all_policies()

            if not policies:
                return "📘 No HR policies available."

            response = "📘 HR POLICIES\n\n"

            for policy in policies:
                title, body = self._split_policy(policy)
                response += f"🟦 {title}\n{body}\n\n"

            return response.strip()

        # ---------- CASE 2: User wants a SPECIFIC policy ----------
        result = self.vector_store.search(query)

        if not result:
            return (
                "📘 I couldn’t find a matching HR policy.\n"
                "You can ask about leave policy, attendance policy, working policy, or code of conduct."
            )

        title, body = self._split_policy(result)
        return f"📘 {title}\n{body}"