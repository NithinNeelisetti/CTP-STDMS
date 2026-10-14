"""Task scheduling algorithms and small pure helper functions."""
from __future__ import annotations
import heapq
from datetime import datetime
from typing import Any, Iterable

def parse_dependencies(value: str | None) -> set[int]:
    """Convert a comma-separated dependency field to a set of task IDs."""
    if not value:
        return set()
    result: set[int] = set()
    for token in value.split(","):
        token = token.strip()
        if token:
            result.add(int(token))
    return result

def priority_label(priority: int) -> str:
    return {1: "Very low", 2: "Low", 3: "Normal", 4: "High", 5: "Urgent"}.get(priority, "Normal")

def completion_rate(tasks: Iterable[dict[str, Any]]) -> float:
    """Return percentage completed; an empty task list has a zero rate."""
    task_list = list(tasks)
    if not task_list:
        return 0.0
    completed = sum(1 for task in task_list if task.get("status") == "Completed")
    return round(100.0 * completed / len(task_list), 1)

def schedule_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Return a dependency-valid task order.

    Kahn's topological-sort algorithm ensures prerequisites come first.
    A heap selects among currently eligible tasks using a greedy policy:
    higher priority, earlier deadline, then lower task ID.
    Complexity: O((V + E) log V), where V is tasks and E is dependency links.
    """
    if not tasks:
        return []
    by_id = {int(task["id"]): task for task in tasks}
    indegree = {task_id: 0 for task_id in by_id}
    outgoing: dict[int, list[int]] = {task_id: [] for task_id in by_id}

    for task_id, task in by_id.items():
        dependencies = parse_dependencies(task.get("dependencies", ""))
        for dependency in dependencies:
            if dependency not in by_id:
                raise ValueError(f"Task {task_id} depends on missing task {dependency}.")
            if dependency == task_id:
                raise ValueError(f"Task {task_id} cannot depend on itself.")
            indegree[task_id] += 1
            outgoing[dependency].append(task_id)

    def heap_key(task_id: int) -> tuple[int, str, int]:
        task = by_id[task_id]
        return (-int(task.get("priority", 3)), str(task.get("deadline", "")), task_id)

    ready: list[tuple[int, str, int]] = []
    for task_id, degree in indegree.items():
        if degree == 0:
            heapq.heappush(ready, heap_key(task_id))

    result: list[dict[str, Any]] = []
    while ready:
        _, _, task_id = heapq.heappop(ready)
        result.append(by_id[task_id])
        for next_id in outgoing[task_id]:
            indegree[next_id] -= 1
            if indegree[next_id] == 0:
                heapq.heappush(ready, heap_key(next_id))

    if len(result) != len(tasks):
        raise ValueError("Circular task dependencies detected. Remove a dependency to continue.")
    return result

def is_overdue(task: dict[str, Any], now: datetime | None = None) -> bool:
    if task.get("status") == "Completed":
        return False
    deadline = datetime.fromisoformat(str(task["deadline"]))
    current = now or datetime.now()
    return deadline < current
