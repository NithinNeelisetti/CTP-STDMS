"""Flask web application for Smart Task and Deadline Management System."""
from __future__ import annotations
import os
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for
from database import DEFAULT_DB, delete_task, get_task, init_db, insert_task, list_tasks, update_task
from scheduler import completion_rate, is_overdue, priority_label, schedule_tasks, parse_dependencies

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-development-secret")
DB_PATH = os.environ.get("TASK_DB_PATH", str(DEFAULT_DB))
init_db(DB_PATH)

def validate_form(form, existing_tasks, current_id=None):
    title = form.get("title", "").strip()
    description = form.get("description", "").strip()
    deadline = form.get("deadline", "").strip()
    try:
        priority = int(form.get("priority", "3"))
        estimated_minutes = int(form.get("estimated_minutes", "30"))
    except ValueError:
        raise ValueError("Priority and estimated duration must be whole numbers.")
    status = form.get("status", "Pending")
    if not title:
        raise ValueError("Task title is required.")
    if priority not in range(1, 6):
        raise ValueError("Priority must be between 1 and 5.")
    if estimated_minutes < 1:
        raise ValueError("Estimated duration must be at least one minute.")
    if status not in {"Pending", "In Progress", "Completed"}:
        raise ValueError("Choose a valid status.")
    try:
        parsed_deadline = datetime.fromisoformat(deadline)
        deadline = parsed_deadline.strftime("%Y-%m-%dT%H:%M")
    except ValueError:
        raise ValueError("Enter a valid deadline.")
    raw_dependencies = form.get("dependencies", "").strip()
    dependency_ids = parse_dependencies(raw_dependencies)
    known_ids = {int(task["id"]) for task in existing_tasks}
    if current_id is not None:
        known_ids.add(int(current_id))
    if current_id in dependency_ids:
        raise ValueError("A task cannot depend on itself.")
    unknown = dependency_ids - known_ids
    if unknown:
        raise ValueError("Unknown dependency task ID(s): " + ", ".join(map(str, sorted(unknown))))
    normalized_dependencies = ",".join(map(str, sorted(dependency_ids)))
    return {"title": title, "description": description, "deadline": deadline,
            "priority": priority, "estimated_minutes": estimated_minutes,
            "status": status, "dependencies": normalized_dependencies}

@app.template_filter("priority_name")
def priority_name_filter(value):
    return priority_label(int(value))

@app.template_filter("pretty_deadline")
def pretty_deadline(value):
    try:
        return datetime.fromisoformat(value).strftime("%d %b %Y, %I:%M %p")
    except (ValueError, TypeError):
        return value

@app.context_processor
def inject_helpers():
    return {"current_year": datetime.now().year}

@app.route("/")
def index():
    tasks = list_tasks(DB_PATH)
    counts = {
        "total": len(tasks),
        "pending": sum(t["status"] == "Pending" for t in tasks),
        "in_progress": sum(t["status"] == "In Progress" for t in tasks),
        "completed": sum(t["status"] == "Completed" for t in tasks),
        "overdue": sum(is_overdue(t) for t in tasks),
        "completion_rate": completion_rate(tasks),
    }
    status_chart = {
        "labels": ["Completed", "In Progress", "Pending"],
        "values": [counts["completed"], counts["in_progress"], counts["pending"]],
    }
    priority_chart = {
        "labels": ["Very low", "Low", "Normal", "High", "Urgent"],
        "values": [sum(int(t["priority"]) == level for t in tasks) for level in range(1, 6)],
    }
    query = request.args.get("q", "").strip().lower()
    status_filter = request.args.get("status", "")
    if query:
        tasks = [t for t in tasks if query in t["title"].lower() or query in t["description"].lower()]
    if status_filter in {"Pending", "In Progress", "Completed"}:
        tasks = [t for t in tasks if t["status"] == status_filter]
    return render_template("index.html", tasks=tasks, counts=counts, q=request.args.get("q", ""),
                           status_filter=status_filter, is_overdue=is_overdue,
                           status_chart=status_chart, priority_chart=priority_chart)

@app.route("/tasks/new", methods=["GET", "POST"])
def create_task():
    if request.method == "POST":
        try:
            data = validate_form(request.form, list_tasks(DB_PATH))
            insert_task(data, DB_PATH)
            flash("Task created successfully.", "success")
            return redirect(url_for("index"))
        except (ValueError, TypeError) as exc:
            flash(str(exc), "error")
            return render_template("task_form.html", task=request.form, tasks=list_tasks(DB_PATH), mode="Create")
    return render_template("task_form.html", task={}, tasks=list_tasks(DB_PATH), mode="Create")

@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    task = get_task(task_id, DB_PATH)
    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("index"))
    if request.method == "POST":
        try:
            existing = list_tasks(DB_PATH)
            data = validate_form(request.form, existing, current_id=task_id)
            # Validate a candidate graph before committing changes, so a cycle is never saved.
            candidate_tasks = [({**item, **data} if int(item["id"]) == task_id else item) for item in existing]
            schedule_tasks(candidate_tasks)
            update_task(task_id, data, DB_PATH)
            flash("Task updated successfully.", "success")
            return redirect(url_for("index"))
        except (ValueError, TypeError) as exc:
            flash(str(exc), "error")
            return render_template("task_form.html", task={**task, **request.form}, tasks=list_tasks(DB_PATH), mode="Edit")
    return render_template("task_form.html", task=task, tasks=list_tasks(DB_PATH), mode="Edit")

@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    task = get_task(task_id, DB_PATH)
    if not task:
        flash("Task not found.", "error")
    else:
        next_status = "Completed" if task["status"] != "Completed" else "Pending"
        update_task(task_id, {**task, "status": next_status}, DB_PATH)
        flash(f"Task marked {next_status.lower()}.", "success")
    return redirect(url_for("index"))

@app.post("/tasks/<int:task_id>/delete")
def remove_task(task_id):
    if delete_task(task_id, DB_PATH):
        flash("Task deleted.", "success")
    else:
        flash("Task not found.", "error")
    return redirect(url_for("index"))

@app.route("/schedule")
def schedule():
    tasks = list_tasks(DB_PATH)
    try:
        scheduled = schedule_tasks([t for t in tasks if t["status"] != "Completed"])
        error = None
    except ValueError as exc:
        scheduled, error = [], str(exc)
    return render_template("schedule.html", scheduled=scheduled, error=error, is_overdue=is_overdue)

@app.route("/health")
def health():
    return {"status": "ok", "application": "Smart Task and Deadline Management System"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=True)
