"""load/save tasks to disk."""
import os
import json

TASKS_FILE = "tasks.json"

# Module-level state — tasks live here in memory
tasks: list = []


def load_tasks() -> None:
    """Read tasks from disk into the module-level `tasks` list (in place)."""
    if not os.path.exists(TASKS_FILE):
        tasks.clear()
        return
    with open(TASKS_FILE, "r") as f:
        loaded = json.load(f)
    tasks.clear()
    tasks.extend(loaded)


def save_tasks() -> None:
    """Write current tasks to disk."""
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)