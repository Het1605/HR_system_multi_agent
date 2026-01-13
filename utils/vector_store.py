# utils/vector_store.py
# Vector database for HR policies using FAISS
# Responsible ONLY for loading, storing, and searching policy text

import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self, policy_file_path: str):
        """
        Initialize vector store.
        """
        self.policy_file_path = policy_file_path
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.documents = []

    def load(self):
        """
        Load policies from file, create embeddings, and build FAISS index.
        Call this ONCE when application starts.
        """
        if not os.path.exists(self.policy_file_path):
            raise FileNotFoundError("HR policy file not found.")

        # Read policy file
        with open(self.policy_file_path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        # Split policies by blank line
        self.documents = [p.strip() for p in text.split("\n\n") if p.strip()]

        if not self.documents:
            raise ValueError("No policies found in HR policy file.")

        # Create embeddings
        embeddings = self.model.encode(self.documents)

        # Convert to numpy array (required by FAISS)
        embeddings = np.array(embeddings).astype("float32")

        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

    def search(self, query: str, top_k: int = 1):
        """
        Search the most relevant policy for a query.
        Returns policy text or None.
        """
        if not query or self.index is None:
            return None

        query_vector = self.model.encode([query])
        query_vector = np.array(query_vector).astype("float32")

        distances, indices = self.index.search(query_vector, top_k)

        if indices.size == 0:
            return None

        best_index = indices[0][0]

        # Safety check
        if best_index < 0 or best_index >= len(self.documents):
            return None

        return self.documents[best_index]