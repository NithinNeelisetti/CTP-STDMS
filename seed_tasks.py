"""
Seed the Smart Task and Deadline Management System with 30 demonstration tasks.

Exactly:
- 15 Completed
- 5 Pending
- 10 In Progress

Run from the project directory:
    python seed_tasks.py

By default this ADDS the 30 demo tasks to the existing database.
To remove existing tasks first and then seed exactly these 30 tasks:
    python seed_tasks.py --reset

The --reset option deletes all current tasks and should only be used on a demo database.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from database import DEFAULT_DB, get_connection, init_db

TASKS = [
    # 15 Completed tasks
    {"title": "Finalize project requirements", "description": "Document the project scope and functional requirements.", "priority": 4, "days": -12, "duration": 45, "status": "Completed", "dependencies": ""},
    {"title": "Create project folder structure", "description": "Set up the application folders and source files.", "priority": 3, "days": -11, "duration": 30, "status": "Completed", "dependencies": ""},
    {"title": "Design database schema", "description": "Define task fields and SQLite table structure.", "priority": 5, "days": -10, "duration": 60, "status": "Completed", "dependencies": ""},
    {"title": "Implement task creation form", "description": "Build the form for adding new tasks.", "priority": 4, "days": -9, "duration": 90, "status": "Completed", "dependencies": ""},
    {"title": "Implement task listing page", "description": "Display tasks in a sortable dashboard table.", "priority": 3, "days": -8, "duration": 75, "status": "Completed", "dependencies": ""},
    {"title": "Add task editing functionality", "description": "Allow users to update task details.", "priority": 3, "days": -7, "duration": 60, "status": "Completed", "dependencies": ""},
    {"title": "Add task deletion functionality", "description": "Allow users to remove tasks safely.", "priority": 2, "days": -6, "duration": 30, "status": "Completed", "dependencies": ""},
    {"title": "Implement priority levels", "description": "Support priority values from 1 to 5.", "priority": 4, "days": -5, "duration": 45, "status": "Completed", "dependencies": ""},
    {"title": "Add deadline validation", "description": "Validate the deadline and estimated duration fields.", "priority": 5, "days": -4, "duration": 50, "status": "Completed", "dependencies": ""},
    {"title": "Create dashboard summary cards", "description": "Show total, pending, in-progress, and completed tasks.", "priority": 3, "days": -3, "duration": 60, "status": "Completed", "dependencies": ""},
    {"title": "Add task search", "description": "Search tasks by title and description.", "priority": 2, "days": -2, "duration": 40, "status": "Completed", "dependencies": ""},
    {"title": "Add status filters", "description": "Filter tasks by their current status.", "priority": 3, "days": -1, "duration": 40, "status": "Completed", "dependencies": ""},
    {"title": "Implement completion-rate calculation", "description": "Calculate the percentage of tasks completed.", "priority": 3, "days": -1, "duration": 35, "status": "Completed", "dependencies": ""},
    {"title": "Add overdue task indicators", "description": "Highlight tasks whose deadlines have passed.", "priority": 4, "days": -1, "duration": 45, "status": "Completed", "dependencies": ""},
    {"title": "Write initial scheduler tests", "description": "Test basic task ordering and dependency handling.", "priority": 4, "days": -1, "duration": 75, "status": "Completed", "dependencies": ""},

    # 5 Pending tasks
    {"title": "Review final project documentation", "description": "Proofread the report and setup instructions.", "priority": 4, "days": 7, "duration": 60, "status": "Pending", "dependencies": ""},
    {"title": "Prepare project defence notes", "description": "Prepare concise explanations of algorithms and design decisions.", "priority": 5, "days": 5, "duration": 90, "status": "Pending", "dependencies": ""},
    {"title": "Capture application screenshots", "description": "Capture dashboard, task form, and smart schedule screens.", "priority": 3, "days": 4, "duration": 45, "status": "Pending", "dependencies": ""},
    {"title": "Review future enhancement ideas", "description": "List possible authentication and notification improvements.", "priority": 2, "days": 10, "duration": 30, "status": "Pending", "dependencies": ""},
    {"title": "Rehearse live demonstration", "description": "Practice the project demo from start to finish.", "priority": 5, "days": 3, "duration": 60, "status": "Pending", "dependencies": ""},

    # 10 In Progress tasks
    {"title": "Implement dependency graph validation", "description": "Validate prerequisite IDs and detect circular dependencies.", "priority": 5, "days": 2, "duration": 120, "status": "In Progress", "dependencies": ""},
    {"title": "Improve smart scheduling policy", "description": "Refine priority and deadline tie-breaking behavior.", "priority": 4, "days": 3, "duration": 90, "status": "In Progress", "dependencies": ""},
    {"title": "Add scheduler edge-case tests", "description": "Test empty lists, missing dependencies, and equal deadlines.", "priority": 4, "days": 4, "duration": 75, "status": "In Progress", "dependencies": ""},
    {"title": "Measure scheduling performance", "description": "Benchmark the scheduler with larger synthetic task sets.", "priority": 3, "days": 6, "duration": 90, "status": "In Progress", "dependencies": ""},
    {"title": "Improve responsive dashboard styling", "description": "Check layout behavior on mobile and desktop widths.", "priority": 3, "days": 5, "duration": 80, "status": "In Progress", "dependencies": ""},
    {"title": "Implement deadline reminder report", "description": "Report overdue tasks and tasks due within 24 hours.", "priority": 4, "days": 2, "duration": 60, "status": "In Progress", "dependencies": ""},
    {"title": "Review database error handling", "description": "Check invalid IDs and missing task records.", "priority": 3, "days": 5, "duration": 60, "status": "In Progress", "dependencies": ""},
    {"title": "Add static type annotations", "description": "Review type hints in application and algorithm modules.", "priority": 2, "days": 8, "duration": 50, "status": "In Progress", "dependencies": ""},
    {"title": "Prepare automated test workflow", "description": "Configure continuous integration to run pytest.", "priority": 3, "days": 7, "duration": 45, "status": "In Progress", "dependencies": ""},
    {"title": "Review security and deployment notes", "description": "Document secret key configuration and development-server limitations.", "priority": 4, "days": 6, "duration": 50, "status": "In Progress", "dependencies": ""},
]

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the task manager with 30 sample tasks.")
    parser.add_argument("--reset", action="store_true", help="Delete existing tasks before inserting the sample tasks.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Optional SQLite database path.")
    args = parser.parse_args()

    init_db(args.db)
    now = datetime.now().replace(second=0, microsecond=0)
    with get_connection(args.db) as conn:
        if args.reset:
            conn.execute("DELETE FROM tasks")
        inserted_ids = []
        for item in TASKS:
            deadline = (now + timedelta(days=item["days"])).strftime("%Y-%m-%dT%H:%M")
            cur = conn.execute(
                """INSERT INTO tasks
                   (title, description, priority, deadline, estimated_minutes, status, dependencies)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (item["title"], item["description"], item["priority"], deadline,
                 item["duration"], item["status"], item["dependencies"]),
            )
            inserted_ids.append(cur.lastrowid)
        conn.commit()

    counts = {"Completed": 0, "Pending": 0, "In Progress": 0}
    for item in TASKS:
        counts[item["status"]] += 1
    print(f"Inserted {len(inserted_ids)} sample tasks into: {args.db}")
    print(f"Completed: {counts['Completed']} | Pending: {counts['Pending']} | In Progress: {counts['In Progress']}")
    print("Open the dashboard and refresh your browser to see the tasks.")

if __name__ == "__main__":
    main()
