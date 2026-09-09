"""
tools/study_plan_tool.py
--------------------------
Generates a simple day-wise study plan for a chosen course by spreading
its topics (from data/courses.json) across the number of days requested
by the student, and stores it in data/study_plans.json.
"""

import uuid
from datetime import datetime
from utils.json_handler import load_json, save_json

STUDY_PLANS_FILE = "data/study_plans.json"


class StudyPlanTool:
    def __init__(self, study_plans_file: str = STUDY_PLANS_FILE):
        self.study_plans_file = study_plans_file
        self.plans = load_json(self.study_plans_file, default={})

    def generate_plan(self, student_id: str, course_id: str, course_info: dict, num_days: int):
        topics = course_info.get("topics", [])
        if not topics:
            return None

        num_days = max(1, num_days)
        plan_id = str(uuid.uuid4())[:8]

        # Distribute topics evenly across the available days
        schedule = {f"Day {i + 1}": [] for i in range(num_days)}
        for i, topic in enumerate(topics):
            day_key = f"Day {(i % num_days) + 1}"
            schedule[day_key].append(topic)

        # If there are more days than topics, mark remaining days as revision
        if num_days > len(topics):
            for i in range(len(topics), num_days):
                schedule[f"Day {i + 1}"] = ["Revision / Practice problems"]

        plan = {
            "plan_id": plan_id,
            "student_id": student_id,
            "course": course_id,
            "course_name": course_info.get("name", course_id),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "num_days": num_days,
            "schedule": schedule
        }

        self.plans[plan_id] = plan
        save_json(self.study_plans_file, self.plans)
        return plan

    @staticmethod
    def print_plan(plan: dict):
        print(f"\n📅 Study Plan for {plan['course_name']} (ID: {plan['plan_id']})")
        print(f"   Duration: {plan['num_days']} day(s)\n")
        for day, topics in plan["schedule"].items():
            topics_str = ", ".join(topics)
            print(f"   {day}: {topics_str}")
        print()
