"""
agent/memory.py
-----------------
Handles all "memory" of the assistant: information about each student
that should persist between runs of the program (name, courses enrolled,
question history, quiz scores, generated study plans).

Everything is stored in data/students.json through utils.json_handler.
"""

from datetime import datetime
from utils.json_handler import load_json, save_json

STUDENTS_FILE = "data/students.json"


class Memory:
    def __init__(self, students_file: str = STUDENTS_FILE):
        self.students_file = students_file
        self.students = load_json(self.students_file, default={})

    # ---------- persistence ----------
    def _save(self):
        save_json(self.students_file, self.students)

    # ---------- student lifecycle ----------
    def student_exists(self, student_id: str) -> bool:
        return student_id in self.students

    def create_student(self, student_id: str, name: str):
        self.students[student_id] = {
            "name": name,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "courses_enrolled": [],
            "question_history": [],
            "quiz_scores": [],
            "study_plans": []
        }
        self._save()

    def get_student(self, student_id: str) -> dict:
        return self.students.get(student_id, {})

    def enroll_course(self, student_id: str, course_id: str):
        student = self.students[student_id]
        if course_id not in student["courses_enrolled"]:
            student["courses_enrolled"].append(course_id)
            self._save()

    # ---------- interaction logging ----------
    def log_question(self, student_id: str, course_id: str, question: str, answer_snippet: str):
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "course": course_id,
            "question": question,
            "answer_snippet": answer_snippet
        }
        self.students[student_id]["question_history"].append(entry)
        self._save()

    def log_quiz_result(self, student_id: str, course_id: str, score: int, total: int, difficulty: str = None):
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "course": course_id,
            "difficulty": difficulty or "mixed",
            "score": score,
            "total": total,
            "percentage": round((score / total) * 100, 2) if total else 0
        }
        self.students[student_id]["quiz_scores"].append(entry)
        self._save()

    def log_study_plan(self, student_id: str, course_id: str, plan_id: str):
        self.students[student_id]["study_plans"].append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "course": course_id,
            "plan_id": plan_id
        })
        self._save()

    # ---------- reporting ----------
    def get_progress_summary(self, student_id: str) -> dict:
        student = self.students.get(student_id, {})
        quiz_scores = student.get("quiz_scores", [])
        avg_score = 0
        if quiz_scores:
            avg_score = round(
                sum(q["percentage"] for q in quiz_scores) / len(quiz_scores), 2
            )
        return {
            "name": student.get("name", "Unknown"),
            "courses_enrolled": student.get("courses_enrolled", []),
            "total_questions_asked": len(student.get("question_history", [])),
            "total_quizzes_taken": len(quiz_scores),
            "average_quiz_score": avg_score,
            "study_plans_generated": len(student.get("study_plans", []))
        }
