# Smart Task and Deadline Management System

A Python web application for creating tasks, setting deadlines, tracking progress, and generating a dependency-aware task schedule.

## Features
- Create, view, edit, search, filter, complete, and delete tasks.
- Priority levels 1–5 and estimated task duration.
- Deadline tracking and overdue indicators.
- Task dependencies using comma-separated task IDs.
- Greedy priority scheduling constrained by prerequisite relationships.
- Dependency-cycle and missing-dependency detection.
- Dashboard counts and completion percentage.
- SQLite persistence.
- Unit tests, a command-line reminder report, and optional Docker support.

## Requirements
- Python 3.10 or later recommended.
- pip.

## Setup
1. Extract the ZIP archive.
2. Open a terminal in the `Smart_Task_Deadline_Management_System` directory.
3. Create and activate a virtual environment:
   - Windows: `python -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the application: `python app.py`
6. Open `http://127.0.0.1:5000` in a browser.
7. Create a task and visit **Smart schedule** to see the scheduling algorithm.

The SQLite database (`tasks.db`) is created automatically on first run.

## Tests
Run:
```bash
pytest -q
```

## Reminder report
Run:
```bash
python cron_reminders.py
```
It prints overdue tasks and tasks due within 24 hours. It does not send email or push notifications. It can be run periodically through cron on Linux/macOS or Task Scheduler on Windows.

## Scheduling policy
The scheduler uses Kahn's topological-sort algorithm to respect dependencies. Among tasks whose prerequisites are already satisfied, a heap prefers higher priority, then earlier deadline, then lower task ID. Complexity is O((V + E) log V) for V tasks and E dependency links. The policy is a heuristic and is not guaranteed to find a globally optimal schedule.

## Quality and security notes
- Set a strong `SECRET_KEY` environment variable before deploying.
- The development server is not intended for public production deployment.
- This student project has no user authentication; do not expose it to the public internet with private task data.
- Input validation and parameterized SQL statements are used.
- Dependencies should be reviewed and pinned before a production deployment.

## Project contents
- `app.py`: Flask routes and form validation.
- `database.py`: SQLite operations.
- `scheduler.py`: scheduling and helper algorithms.
- `templates/`: HTML templates.
- `static/style.css`: responsive styling.
- `tests/`: automated unit tests.
- `cron_reminders.py`: command-line deadline report.
- `IMPLEMENTATION_GUIDE.md`: step-by-step implementation.
- `report.pdf`: project report.
- `presentation.pptx`: project defence presentation.
