"""Tool functions Andy can call, plus the tool schemas for Claude."""
from storage import tasks, save_tasks


# ---- Tool functions ----

def add_task(description: str) -> str:
    tasks.append({"description": description, "done": False})
    save_tasks()
    return f"Added task: '{description}'. You now have {len(tasks)} task(s)."


def list_tasks() -> str:
    if not tasks:
        return "You have no tasks."
    lines = []
    for i, task in enumerate(tasks):
        status = "[x]" if task["done"] else "[ ]"
        lines.append(f"{i + 1}. {status} {task['description']}")
    return "\n".join(lines)


def complete_task(task_number: int) -> str:
    index = task_number - 1
    if index < 0 or index >= len(tasks):
        return f"Error: no task numbered {task_number}. You have {len(tasks)} task(s)."
    if tasks[index]["done"]:
        return f"Task {task_number} is already done."
    tasks[index]["done"] = True
    save_tasks()
    return f"Marked '{tasks[index]['description']}' as done."


def clear_all_tasks() -> str:
    count = len(tasks)
    tasks.clear()
    save_tasks()
    return f"Cleared all {count} task(s)."


# ---- Dispatcher: maps tool names → real functions ----

def run_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "add_task":
        return add_task(**tool_input)
    if tool_name == "list_tasks":
        return list_tasks(**tool_input)
    if tool_name == "complete_task":
        return complete_task(**tool_input)
    if tool_name == "clear_all_tasks":
        return clear_all_tasks(**tool_input)
    return f"Error: unknown tool '{tool_name}'"


# ---- Tool schemas (what Claude sees) ----

TOOL_SCHEMAS = [
    {
        "name": "add_task",
        "description": "Add a new task to the user's to-do list. Use this whenever the user wants to remember something or note something to do.",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "A short description of the task."}
            },
            "required": ["description"]
        }
    },
    {
        "name": "list_tasks",
        "description": "Show all the user's current tasks with their numbers and completion status. Use this when the user asks what they need to do, wants to see their list, or asks about their tasks.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "complete_task",
        "description": "Mark a specific task as done by its number (1-based, as shown to the user). If the user describes a task by content (e.g. 'I finished the groceries one') and you don't know the number, call list_tasks first to see the numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_number": {"type": "integer", "description": "The task number to mark complete (1-based)."}
            },
            "required": ["task_number"]
        }
    },
    {
        "name": "clear_all_tasks",
        "description": "Delete ALL tasks from the list. Only use this when the user clearly wants to wipe everything (e.g. 'clear my list', 'start over'). Never use this for partial deletions.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    }
]