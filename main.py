"""
main.py
--------
Terminal entry point for the AI Learning & Study Assistant.

Run with:
    python main.py

Everything (student profiles, quiz results, study plans, question
history) is persisted as JSON under the data/ folder, so progress
survives between runs.
"""

import sys
import re
import unicodedata
from agent.assistant import StudyAssistant

LINE = "=" * 60


def clean_input(prompt: str) -> str:
    """
    A safer replacement for input().strip() that also removes:
      - Windows carriage-return leftovers (\\r)
      - Byte-order-mark / zero-width characters some editors/terminals add
      - Full-width digits (e.g. typed via a phone keyboard: １２３ -> 123)
    This is the main fix for "whatever I type says Invalid" issues, which
    almost always come from hidden characters riding along with the input.
    """
    raw = input(prompt)
    raw = raw.replace("\r", "").replace("\ufeff", "").replace("\u200b", "")
    raw = unicodedata.normalize("NFKC", raw)  # full-width digits -> normal digits
    return raw.strip()


def to_int(text: str, default: int = None):
    """Extract the first integer found in `text`. Returns `default` if none found."""
    match = re.search(r"\d+", text)
    if match:
        return int(match.group())
    return default


def banner():
    print(LINE)
    print("   🎓  AI LEARNING & STUDY ASSISTANT  🎓")
    print(LINE)


def print_menu():
    print("\nWhat would you like to do?")
    print(" 1. 📚 View available courses")
    print(" 2. 🤖 Ask a question (search study material)")
    print(" 3. 📝 Take a quiz")
    print(" 4. 📅 Generate a study plan")
    print(" 5. 📊 View my progress")
    print(" 6. 🚪 Exit")


def choose_course(assistant: StudyAssistant):
    courses = assistant.list_courses()
    print("\nAvailable courses:")
    course_ids = list(courses.keys())
    for i, cid in enumerate(course_ids, start=1):
        print(f"  {i}. {courses[cid]['name']}  (id: {cid})")

    choice = clean_input("Choose a course number: ")
    num = to_int(choice)
    if num is None or not (1 <= num <= len(course_ids)):
        print(f"Invalid choice: '{choice}'. Please enter a number between 1 and {len(course_ids)}.")
        return None
    return course_ids[num - 1]


def show_courses(assistant: StudyAssistant):
    courses = assistant.list_courses()
    print("\n📚 Available Courses")
    print("-" * 60)
    for cid, info in courses.items():
        print(f"• {info['name']}  (id: {cid})  |  Difficulty: {info['difficulty']}")
        print(f"    Topics: {', '.join(info['topics'])}")
    print("-" * 60)


def handle_question(assistant: StudyAssistant, student_id: str):
    course_id = choose_course(assistant)
    if not course_id:
        return
    question = clean_input("\nType your question: ")
    if not question:
        print("Question cannot be empty.")
        return

    print("\n🔎 Searching study material...\n")
    answer = assistant.ask_question(student_id, course_id, question)
    print(answer)


def choose_difficulty(assistant: StudyAssistant, course_id: str) -> str:
    levels = assistant.quiz_tool.available_difficulties(course_id)
    if not levels:
        return None

    print("\nChoose a difficulty:")
    options = levels + ["mixed (all levels)"]
    for i, label in enumerate(options, start=1):
        print(f"  {i}. {label.capitalize()}")

    choice = clean_input(f"Enter choice (1-{len(options)}, default {len(options)}): ")
    num = to_int(choice, default=len(options))
    if num is None or not (1 <= num <= len(options)):
        num = len(options)

    return None if num == len(options) else levels[num - 1]


def handle_quiz(assistant: StudyAssistant, student_id: str):
    course_id = choose_course(assistant)
    if not course_id:
        return
    if not assistant.quiz_tool.has_questions(course_id):
        print("No quiz available for this course yet.")
        return

    difficulty = choose_difficulty(assistant, course_id)
    num_q = to_int(clean_input("How many questions? (default 5): "), default=5)

    assistant.enroll(student_id, course_id)
    score, total = assistant.take_quiz(student_id, course_id, num_q, difficulty)
    if total:
        pct = round((score / total) * 100, 1)
        print(f"📈 You scored {pct}% this attempt.")


def handle_study_plan(assistant: StudyAssistant, student_id: str):
    course_id = choose_course(assistant)
    if not course_id:
        return
    days = to_int(clean_input("How many days do you want to plan for? (default 7): "), default=7)

    assistant.enroll(student_id, course_id)
    plan = assistant.generate_study_plan(student_id, course_id, days)
    if plan:
        assistant.study_plan_tool.print_plan(plan)
    else:
        print("Could not generate a study plan for this course.")


def handle_progress(assistant: StudyAssistant, student_id: str):
    progress = assistant.get_progress(student_id)
    print("\n📊 Your Progress Summary")
    print("-" * 60)
    print(f"Name                     : {progress['name']}")
    print(f"Courses enrolled         : {', '.join(progress['courses_enrolled']) or 'None yet'}")
    print(f"Questions asked so far   : {progress['total_questions_asked']}")
    print(f"Quizzes taken            : {progress['total_quizzes_taken']}")
    print(f"Average quiz score       : {progress['average_quiz_score']}%")
    print(f"Study plans generated    : {progress['study_plans_generated']}")
    print("-" * 60)


def login(assistant: StudyAssistant) -> str:
    print("\n👋 Welcome! Let's get you set up.")
    student_id = clean_input("Enter your student ID (e.g. roll number/email): ")
    while not student_id:
        student_id = clean_input("Student ID cannot be empty. Try again: ")

    if assistant.memory.student_exists(student_id):
        student = assistant.memory.get_student(student_id)
        print(f"\n✅ Welcome back, {student['name']}!")
    else:
        name = clean_input("Looks like you're new here. What's your name? ") or student_id
        assistant.login_or_register(student_id, name)
        print(f"\n✅ Account created. Welcome, {name}!")

    return student_id


def main():
    banner()
    assistant = StudyAssistant()
    student_id = login(assistant)

    while True:
        print_menu()
        raw_choice = clean_input("Enter choice (1-6): ")
        choice = to_int(raw_choice)

        if choice == 1:
            show_courses(assistant)
        elif choice == 2:
            handle_question(assistant, student_id)
        elif choice == 3:
            handle_quiz(assistant, student_id)
        elif choice == 4:
            handle_study_plan(assistant, student_id)
        elif choice == 5:
            handle_progress(assistant, student_id)
        elif choice == 6:
            print("\n👋 Goodbye! Keep learning. Your progress has been saved.")
            sys.exit(0)
        else:
            print(f"Invalid choice: '{raw_choice}'. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted. Your progress up to this point is saved. Bye!")
        sys.exit(0)
