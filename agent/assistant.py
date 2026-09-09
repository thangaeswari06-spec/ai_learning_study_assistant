"""
agent/assistant.py
---------------------
The "brain" of the AI Learning & Study Assistant.

StudyAssistant ties together:
  - Memory (student profiles / history, JSON-backed)
  - RAGEngine (retrieval over knowledge_base/*.txt)
  - Tools (search_tool, quiz_tool, study_plan_tool)

main.py only talks to this class - it never touches memory, rag or tools
directly. This keeps the CLI layer thin and the logic reusable.
"""

from utils.json_handler import load_json
from agent.memory import Memory
from agent.rag import RAGEngine
from tools.search_tool import SearchTool
from tools.quiz_tool import QuizTool
from tools.study_plan_tool import StudyPlanTool

COURSES_FILE = "data/courses.json"


class StudyAssistant:
    def __init__(self):
        self.courses = load_json(COURSES_FILE, default={})
        self.memory = Memory()
        self.rag = RAGEngine()
        self.search_tool = SearchTool(self.rag)
        self.quiz_tool = QuizTool()
        self.study_plan_tool = StudyPlanTool()

    # ---------- student management ----------
    def login_or_register(self, student_id: str, name: str = None):
        if self.memory.student_exists(student_id):
            return self.memory.get_student(student_id), False
        else:
            self.memory.create_student(student_id, name or student_id)
            return self.memory.get_student(student_id), True

    def enroll(self, student_id: str, course_id: str):
        self.memory.enroll_course(student_id, course_id)

    # ---------- course info ----------
    def list_courses(self):
        return self.courses

    def course_exists(self, course_id: str) -> bool:
        return course_id in self.courses

    def get_course(self, course_id: str) -> dict:
        return self.courses.get(course_id, {})

    # ---------- Q&A (RAG) ----------
    def ask_question(self, student_id: str, course_id: str, question: str):
        answer, snippet = self.search_tool.answer_question(question, course_id=course_id)
        self.memory.log_question(student_id, course_id, question, snippet)
        return answer

    # ---------- quiz ----------
    def take_quiz(self, student_id: str, course_id: str, num_questions: int = 5):
        score, total = self.quiz_tool.run_quiz(course_id, num_questions)
        if total > 0:
            self.memory.log_quiz_result(student_id, course_id, score, total)
        return score, total

    # ---------- study plan ----------
    def generate_study_plan(self, student_id: str, course_id: str, num_days: int):
        course_info = self.get_course(course_id)
        plan = self.study_plan_tool.generate_plan(student_id, course_id, course_info, num_days)
        if plan:
            self.memory.log_study_plan(student_id, course_id, plan["plan_id"])
        return plan

    # ---------- progress ----------
    def get_progress(self, student_id: str):
        return self.memory.get_progress_summary(student_id)
