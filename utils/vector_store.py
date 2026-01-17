# utils/vector_store.py
# Vector database for HR policies using FAISS
# Handles badly formatted (character-per-line) text safely

import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self, policy_file_path: str):
        self.policy_file_path = policy_file_path
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.documents = []

    def load(self):
        """
        Load policies from file, split by POLICY headings,
        create embeddings, and build FAISS index.
        """
        if not os.path.exists(self.policy_file_path):
            raise FileNotFoundError("HR policy file not found.")

        with open(self.policy_file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # 🔥 CRITICAL FIX: split by POLICY titles
        raw_policies = []
        buffer = ""

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            # Detect policy heading
            if line.isupper() and "POLICY" in line or line == "CODE OF CONDUCT":
                if buffer:
                    raw_policies.append(buffer.strip())
                    buffer = ""
                buffer = line
            else:
                buffer += " " + line

        if buffer:
            raw_policies.append(buffer.strip())

        self.documents = raw_policies

        if not self.documents:
            raise ValueError("No HR policies found.")

        embeddings = self.model.encode(self.documents)
        embeddings = np.array(embeddings).astype("float32")

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

    # -------------------------
    # Return ALL policies
    # -------------------------
    def get_all_policies(self):
        return self.documents

    # -------------------------
    # Semantic search
    # -------------------------
    def search(self, query: str, top_k: int = 1):
        if not query or self.index is None:
            return None

        q_vec = self.model.encode([query])
        q_vec = np.array(q_vec).astype("float32")

        _, indices = self.index.search(q_vec, top_k)
        idx = indices[0][0]

        if idx < 0 or idx >= len(self.documents):
            return None

        return self.documents[idx]