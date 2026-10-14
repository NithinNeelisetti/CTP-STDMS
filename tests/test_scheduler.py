from datetime import datetime
import pytest
from scheduler import completion_rate, is_overdue, parse_dependencies, schedule_tasks

def sample_tasks():
    return [
        {"id": 1, "title": "Write outline", "priority": 2, "deadline": "2027-01-10T10:00", "dependencies": ""},
        {"id": 2, "title": "Write report", "priority": 5, "deadline": "2027-01-09T10:00", "dependencies": "1"},
        {"id": 3, "title": "Prepare slides", "priority": 4, "deadline": "2027-01-08T10:00", "dependencies": ""},
    ]

def test_dependencies_come_before_dependents():
    result = schedule_tasks(sample_tasks())
    positions = {task["id"]: index for index, task in enumerate(result)}
    assert positions[1] < positions[2]

def test_priority_selects_among_available_tasks():
    result = schedule_tasks(sample_tasks())
    assert result[0]["id"] == 3

def test_cycle_is_detected():
    tasks = [
        {"id": 1, "priority": 3, "deadline": "2027-01-01T10:00", "dependencies": "2"},
        {"id": 2, "priority": 3, "deadline": "2027-01-02T10:00", "dependencies": "1"},
    ]
    with pytest.raises(ValueError, match="Circular"):
        schedule_tasks(tasks)

def test_missing_dependency_is_reported():
    tasks = [{"id": 1, "priority": 3, "deadline": "2027-01-01T10:00", "dependencies": "99"}]
    with pytest.raises(ValueError, match="missing task"):
        schedule_tasks(tasks)

def test_parse_dependencies():
    assert parse_dependencies("1, 3,3") == {1, 3}
    assert parse_dependencies("") == set()

def test_completion_rate():
    assert completion_rate([]) == 0.0
    assert completion_rate([{"status": "Completed"}, {"status": "Pending"}]) == 50.0

def test_completed_tasks_are_not_overdue():
    task = {"status": "Completed", "deadline": "2020-01-01T00:00"}
    assert not is_overdue(task, datetime(2027, 1, 1))
