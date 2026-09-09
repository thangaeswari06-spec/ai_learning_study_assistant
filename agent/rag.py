"""
agent/rag.py
-------------
A lightweight, dependency-free RAG (Retrieval-Augmented Generation) style
search engine.

How it works:
1. Each knowledge_base/*.txt file is split into paragraph-level "chunks".
2. Every chunk is converted into a bag-of-words term-frequency vector.
3. A user query is converted into the same kind of vector.
4. Cosine similarity ranks chunks against the query.
5. The best matching chunk(s) are returned as the "retrieved context",
   which the assistant then uses to answer the student's question.

No external ML libraries are required - everything is implemented with
plain Python so the project runs anywhere Python 3 runs.
"""

import os
import re
import math
from collections import Counter

STOPWORDS = {
    "the", "is", "a", "an", "of", "and", "to", "in", "on", "for", "it",
    "this", "that", "are", "was", "were", "be", "as", "by", "with", "or",
    "at", "from", "which", "can", "into", "these", "such", "also", "its",
    "used", "using", "use", "than", "then", "so", "do", "does", "how",
    "what", "when", "where", "why", "who"
}


def stem(word: str) -> str:
    """
    Very small, dependency-free suffix stripper (not a real linguistic
    stemmer, just enough to fix the common mismatch where a student asks
    about "variable" but the notes say "variables", or asks about
    "functions" but the notes say "function").

    This is the fix for the bug where relevant notes existed in the
    knowledge base but the Q&A feature reported "nothing found" just
    because the word form didn't match exactly.
    """
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    if len(word) > 5 and word.endswith("ing"):
        return word[:-3]
    if len(word) > 4 and word.endswith("ed"):
        return word[:-2]
    return word


def tokenize(text: str):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [stem(w) for w in words if w not in STOPWORDS and len(w) > 1]


class RAGEngine:
    def __init__(self, knowledge_base_dir: str = "knowledge_base"):
        self.knowledge_base_dir = knowledge_base_dir
        # course_id -> list of chunk dicts {"text":.., "vector":Counter, "norm": float}
        self.index = {}
        self._build_index()

    # ---------- index construction ----------
    def _build_index(self):
        if not os.path.isdir(self.knowledge_base_dir):
            return

        for filename in os.listdir(self.knowledge_base_dir):
            if not filename.endswith(".txt"):
                continue
            course_id = filename.replace(".txt", "")
            path = os.path.join(self.knowledge_base_dir, filename)

            with open(path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            # Split into paragraphs -> chunks
            paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
            chunks = []
            for para in paragraphs:
                tokens = tokenize(para)
                if not tokens:
                    continue
                vector = Counter(tokens)
                norm = math.sqrt(sum(v * v for v in vector.values()))
                chunks.append({"text": para, "vector": vector, "norm": norm})

            self.index[course_id] = chunks

    # ---------- similarity ----------
    @staticmethod
    def _cosine_similarity(vec_a: Counter, norm_a: float, vec_b: Counter, norm_b: float) -> float:
        if norm_a == 0 or norm_b == 0:
            return 0.0
        common_terms = set(vec_a.keys()) & set(vec_b.keys())
        dot_product = sum(vec_a[t] * vec_b[t] for t in common_terms)
        return dot_product / (norm_a * norm_b)

    # ---------- public search API ----------
    def search(self, query: str, course_id: str = None, top_k: int = 2):
        """
        Search the knowledge base for chunks most relevant to `query`.
        If `course_id` is given, restrict the search to that course's file,
        otherwise search across all courses.
        Returns a list of dicts: {"course", "text", "score"} sorted by score desc.
        """
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        query_vector = Counter(query_tokens)
        query_norm = math.sqrt(sum(v * v for v in query_vector.values()))

        courses_to_search = [course_id] if course_id else list(self.index.keys())
        results = []

        for cid in courses_to_search:
            for chunk in self.index.get(cid, []):
                score = self._cosine_similarity(
                    query_vector, query_norm, chunk["vector"], chunk["norm"]
                )
                if score > 0:
                    results.append({"course": cid, "text": chunk["text"], "score": round(score, 4)})

        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    def available_courses(self):
        return list(self.index.keys())
