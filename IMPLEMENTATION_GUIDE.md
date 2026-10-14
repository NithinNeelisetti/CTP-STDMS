# Step-by-Step Implementation Guide

## Step 1 — Define the problem
Students often track assignments and deadlines in separate places. This makes prioritization difficult and can hide overdue tasks or prerequisite relationships. The system provides one place to manage work and recommend a valid task order.

## Step 2 — Define inputs and outputs
Inputs: title, description, priority (1–5), deadline, estimated duration, status, and optional prerequisite task IDs.
Outputs: dashboard counts, overdue labels, completion rate, and a dependency-valid recommended schedule.

## Step 3 — Prepare the environment
Install Python 3.10+, create a virtual environment, and run `pip install -r requirements.txt`.

## Step 4 — Understand the architecture
- `app.py` receives browser requests, validates form data, and renders pages.
- `database.py` stores and retrieves records in SQLite using parameterized queries.
- `scheduler.py` contains pure helper functions and the scheduling algorithm.
- `templates/` contains the pages.
- `static/style.css` contains the presentation layer.
- `tests/` verifies algorithm correctness and edge cases.

## Step 5 — Run the web application
Run `python app.py` and open `http://127.0.0.1:5000`. Create tasks with different priorities and deadlines.

## Step 6 — Test CRUD operations
Create a task, edit its fields, mark it complete, reopen it, search/filter tasks, and delete a task. Confirm dashboard counts change.

## Step 7 — Test the scheduler
Create a prerequisite task and another task that depends on its ID. Open Smart schedule and confirm the prerequisite appears first. Test a cycle through unit tests; the scheduler should reject circular dependencies.

## Step 8 — Run automated tests
Run `pytest -q`. The included tests cover prerequisite order, priority ordering among eligible tasks, cycles, missing dependencies, dependency parsing, completion rate, and overdue status.

## Step 9 — Evaluate complexity and performance
The scheduler performs a topological ordering while using a heap to select eligible tasks. Its stated complexity is O((V + E) log V), where V is the task count and E is the dependency count. For a defence, benchmark several synthetic task sizes, record actual timings, and distinguish measured results from theoretical bounds.

## Step 10 — Run the reminder report
Run `python cron_reminders.py`. It prints tasks that are overdue or due within 24 hours. For automation, schedule this command using cron or Windows Task Scheduler. Email delivery is not implemented by default.

## Step 11 — Quality checks
Use `pytest`, `ruff check .`, and `mypy app.py scheduler.py database.py` after installing the optional tools. Review warnings rather than claiming quality solely from a successful run.

## Step 12 — Prepare the defence
Demonstrate the dashboard, CRUD, scheduling order, dependency handling, tests, complexity, and reminder report. Explain that the priority scheduler is a practical heuristic rather than a proof of global optimality.

## Suggested 8–10 minute demonstration chronology
1. 0:00–1:00 — Problem statement and objectives.
2. 1:00–2:00 — Dashboard and data model.
3. 2:00–4:00 — Create tasks and demonstrate scheduling.
4. 4:00–5:00 — Dependencies and cycle handling.
5. 5:00–6:00 — Dashboard metrics and overdue tasks.
6. 6:00–7:30 — Automated tests and complexity.
7. 7:30–8:30 — Reminder report and quality practices.
8. 8:30–10:00 — Limitations, future enhancements, and questions.
