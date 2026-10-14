"""Command-line reminder report; schedule this script with cron/Task Scheduler if desired."""
from datetime import datetime, timedelta
from database import DEFAULT_DB, init_db, list_tasks
import os

def main():
    db_path = os.environ.get("TASK_DB_PATH", str(DEFAULT_DB))
    init_db(db_path)
    now = datetime.now()
    soon = now + timedelta(hours=24)
    tasks = list_tasks(db_path)
    matches = []
    for task in tasks:
        if task["status"] == "Completed":
            continue
        try:
            deadline = datetime.fromisoformat(task["deadline"])
        except ValueError:
            continue
        if deadline < now:
            matches.append(("OVERDUE", task))
        elif deadline <= soon:
            matches.append(("DUE WITHIN 24 HOURS", task))
    if not matches:
        print("No overdue tasks or tasks due in the next 24 hours.")
        return
    for label, task in matches:
        print(f"[{label}] #{task['id']} {task['title']} — deadline {task['deadline']} — priority {task['priority']}")

if __name__ == "__main__":
    main()
