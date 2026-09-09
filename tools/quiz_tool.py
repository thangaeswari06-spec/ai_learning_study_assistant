"""
tools/quiz_tool.py
--------------------
Generates and runs an interactive multiple-choice quiz in the terminal
for a chosen course, using the question bank in data/quiz_data.json.
"""

import random
from utils.json_handler import load_json

QUIZ_DATA_FILE = "data/quiz_data.json"


class QuizTool:
    def __init__(self, quiz_data_file: str = QUIZ_DATA_FILE):
        self.quiz_data = load_json(quiz_data_file, default={})

    def has_questions(self, course_id: str) -> bool:
        return bool(self.quiz_data.get(course_id))

    def generate_quiz(self, course_id: str, num_questions: int = 5):
        """Return a shuffled list of up to `num_questions` questions for the course."""
        pool = self.quiz_data.get(course_id, [])
        num_questions = min(num_questions, len(pool))
        return random.sample(pool, num_questions) if pool else []

    def run_quiz(self, course_id: str, num_questions: int = 5):
        """
        Runs the quiz fully interactively in the terminal.
        Returns (score, total_questions).
        """
        questions = self.generate_quiz(course_id, num_questions)
        if not questions:
            print("No quiz questions available for this course yet.")
            return 0, 0

        score = 0
        print(f"\n📝 Starting quiz — {len(questions)} questions. Type the option number.\n")

        for idx, q in enumerate(questions, start=1):
            print(f"Q{idx}. {q['question']}")
            options = q["options"][:]
            random.shuffle(options)
            for opt_idx, opt in enumerate(options, start=1):
                print(f"   {opt_idx}. {opt}")

            user_choice = input("Your answer (number): ").strip()
            try:
                chosen_answer = options[int(user_choice) - 1]
            except (ValueError, IndexError):
                chosen_answer = None

            if chosen_answer == q["answer"]:
                print("✅ Correct!\n")
                score += 1
            else:
                print(f"❌ Wrong. Correct answer: {q['answer']}\n")

        print(f"🏁 Quiz finished! Score: {score}/{len(questions)}")
        return score, len(questions)
