# agents/knowledge_agent.py
# Knowledge agent using Vector DB (FAISS) for HR policies

from utils.vector_store import VectorStore


class KnowledgeAgent:
    def __init__(self):
        """
        Initialize vector store and load HR policies.
        """
        self.vector_store = VectorStore("data/hr_policy.txt")
        self.vector_store.load()

    def search_policy(self, query: str):
        """
        Search HR policy using semantic vector search.
        Returns policy text or None.
        """
        if not query:
            return None

        result = self.vector_store.search(query)

        if not result:
            return None

        return f"📘 {result}"