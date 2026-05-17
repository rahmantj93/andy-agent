"""Unit tests for Andy's tool functions (the deterministic, non-AI layer)."""
import pytest

from storage import tasks
from tools import (
    add_task,
    list_tasks,
    complete_task,
    update_task,
    get_priorities,
    clear_all_tasks,
)


@pytest.fixture(autouse=True)
def clean_state(tmp_path, monkeypatch):
    """
    Before each test:
    - Redirect storage to a temporary file (never touches the real tasks.json)
    - Start with an empty task list
    After each test: clear the list again.
    """
    import storage
    temp_file = tmp_path / "tasks_test.json"
    monkeypatch.setattr(storage, "TASKS_FILE", str(temp_file))
    tasks.clear()
    yield
    tasks.clear()


# ---- add_task ----

def test_add_task_increases_count():
    result = add_task("buy milk")
    assert len(tasks) == 1
    assert "1 task(s)" in result


def test_add_task_stores_due_and_priority():
    add_task("finish essay", due="Friday", priority="high")
    task = tasks[0]
    assert task["description"] == "finish essay"
    assert task["due"] == "Friday"
    assert task["priority"] == "high"
    assert task["done"] is False


# ---- list_tasks ----

def test_list_tasks_empty():
    assert list_tasks() == "You have no tasks."


def test_list_tasks_shows_annotations():
    add_task("plain task")
    add_task("urgent task", due="Monday", priority="high")
    output = list_tasks()
    assert "plain task" in output
    assert "priority: high" in output
    assert "due: Monday" in output


# ---- complete_task ----

def test_complete_task_marks_done():
    add_task("task one")
    result = complete_task(1)
    assert tasks[0]["done"] is True
    assert "done" in result.lower()


def test_complete_task_invalid_number():
    add_task("only task")
    result = complete_task(99)
    assert "Error" in result
    assert tasks[0]["done"] is False


# ---- update_task ----

def test_update_task_changes_priority_only():
    add_task("coursework", due="Monday", priority="low")
    update_task(1, priority="high")
    assert tasks[0]["priority"] == "high"
    assert tasks[0]["due"] == "Monday"          # unchanged
    assert tasks[0]["description"] == "coursework"  # unchanged


def test_update_task_nothing_provided():
    add_task("a task")
    result = update_task(1)
    assert "Nothing to update" in result


# ---- get_priorities ----

def test_get_priorities_empty():
    result = get_priorities()
    assert "no pending tasks" in result.lower()


def test_get_priorities_lists_pending():
    add_task("important", priority="high", due="tomorrow")
    result = get_priorities()
    assert "important" in result
    assert "high" in result