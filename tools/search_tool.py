"""
tools/search_tool.py
----------------------
Wraps agent.rag.RAGEngine as a "tool" the assistant can call when a
student asks a question. Responsible for formatting the retrieved
chunks into a readable terminal answer.
"""


class SearchTool:
    def __init__(self, rag_engine):
        self.rag = rag_engine

    def answer_question(self, question: str, course_id: str = None):
        """
        Retrieve the most relevant knowledge-base chunks for `question`
        and build a simple, readable answer out of them.
        Returns (answer_text, best_snippet_for_logging).
        """
        results = self.rag.search(question, course_id=course_id, top_k=2)

        if not results:
            return (
                "Sorry, I couldn't find anything relevant in the knowledge base "
                "for that question. Try rephrasing it or pick a different course.",
                ""
            )

        answer_lines = ["Here's what I found in the study material:\n"]
        for i, r in enumerate(results, start=1):
            confidence = f"{r['score'] * 100:.1f}%"
            answer_lines.append(
                f"[{i}] (course: {r['course']}, relevance: {confidence})\n    {r['text']}\n"
            )

        best_snippet = results[0]["text"][:150] + ("..." if len(results[0]["text"]) > 150 else "")
        return "\n".join(answer_lines), best_snippet
