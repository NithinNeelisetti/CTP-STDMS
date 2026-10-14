"""SQLite persistence layer for Smart Task and Deadline Management System."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB = Path(__file__).resolve().parent / "tasks.db"

def get_connection(db_path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(db_path: str | Path = DEFAULT_DB) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                priority INTEGER NOT NULL DEFAULT 3 CHECK(priority BETWEEN 1 AND 5),
                deadline TEXT NOT NULL,
                estimated_minutes INTEGER NOT NULL DEFAULT 30 CHECK(estimated_minutes > 0),
                status TEXT NOT NULL DEFAULT 'Pending'
                    CHECK(status IN ('Pending', 'In Progress', 'Completed')),
                dependencies TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def list_tasks(db_path: str | Path = DEFAULT_DB) -> list[dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY deadline, id").fetchall()
    return [dict(row) for row in rows]

def get_task(task_id: int, db_path: str | Path = DEFAULT_DB) -> dict[str, Any] | None:
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return dict(row) if row else None

def insert_task(task: dict[str, Any], db_path: str | Path = DEFAULT_DB) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute("""
            INSERT INTO tasks (title, description, priority, deadline, estimated_minutes, status, dependencies)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (task["title"], task.get("description", ""), task["priority"], task["deadline"],
              task["estimated_minutes"], task.get("status", "Pending"), task.get("dependencies", "")))
        conn.commit()
        return int(cur.lastrowid)

def update_task(task_id: int, task: dict[str, Any], db_path: str | Path = DEFAULT_DB) -> bool:
    with get_connection(db_path) as conn:
        cur = conn.execute("""
            UPDATE tasks
            SET title=?, description=?, priority=?, deadline=?, estimated_minutes=?, status=?, dependencies=?
            WHERE id=?
        """, (task["title"], task.get("description", ""), task["priority"], task["deadline"],
              task["estimated_minutes"], task.get("status", "Pending"), task.get("dependencies", ""), task_id))
        conn.commit()
        return cur.rowcount > 0

def delete_task(task_id: int, db_path: str | Path = DEFAULT_DB) -> bool:
    with get_connection(db_path) as conn:
        # Remove references to the deleted task before deleting it.
        rows = conn.execute("SELECT id, dependencies FROM tasks WHERE id != ?", (task_id,)).fetchall()
        for row in rows:
            deps = [part.strip() for part in row["dependencies"].split(",") if part.strip()]
            filtered = [part for part in deps if part != str(task_id)]
            if filtered != deps:
                conn.execute("UPDATE tasks SET dependencies=? WHERE id=?", (",".join(filtered), row["id"]))
        cur = conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        return cur.rowcount > 0
