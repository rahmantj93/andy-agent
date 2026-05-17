"""Tool functions Andy can call, plus the tool schemas for Claude."""
from storage import tasks, save_tasks


# ---- Tool functions ----

def add_task(description: str, due: str = None, priority: str = None) -> str:
    task = {
        "description": description,
        "done": False,
        "due": due,            # e.g. "Friday", "2026-05-25", or None
        "priority": priority,  # "high", "medium", "low", or None
    }
    tasks.append(task)
    save_tasks()

    # Build a confirmation that mentions due/priority only if they were given
    extras = []
    if due:
        extras.append(f"due {due}")
    if priority:
        extras.append(f"{priority} priority")
    suffix = f" ({', '.join(extras)})" if extras else ""

    return f"Added task: '{description}'{suffix}. You now have {len(tasks)} task(s)."


def list_tasks() -> str:
    if not tasks:
        return "You have no tasks."
    lines = []
    for i, task in enumerate(tasks):
        status = "[x]" if task["done"] else "[ ]"

        # Build optional annotations, safely handling old tasks missing these keys
        annotations = []
        due = task.get("due")
        priority = task.get("priority")
        if priority:
            annotations.append(f"priority: {priority}")
        if due:
            annotations.append(f"due: {due}")

        suffix = f"  ({', '.join(annotations)})" if annotations else ""
        lines.append(f"{i + 1}. {status} {task['description']}{suffix}")
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


def update_task(task_number: int, description: str = None,
                 due: str = None, priority: str = None) -> str:
    index = task_number - 1
    if index < 0 or index >= len(tasks):
        return f"Error: no task numbered {task_number}. You have {len(tasks)} task(s)."

    task = tasks[index]
    changes = []

    if description is not None:
        task["description"] = description
        changes.append(f"description → '{description}'")
    if due is not None:
        task["due"] = due
        changes.append(f"due → {due}")
    if priority is not None:
        task["priority"] = priority
        changes.append(f"priority → {priority}")

    if not changes:
        return "Nothing to update — no new values provided."

    save_tasks()
    return f"Updated task {task_number}: {', '.join(changes)}."

def get_priorities() -> str:
    """Return a structured summary of unfinished tasks for Claude to reason about."""
    pending = [t for t in tasks if not t["done"]]
    if not pending:
        return "There are no pending tasks. The user is all caught up."

    lines = ["Here are the pending tasks with their metadata:"]
    for i, task in enumerate(tasks):
        if task["done"]:
            continue
        due = task.get("due") or "no due date"
        priority = task.get("priority") or "no priority set"
        lines.append(
            f"- Task {i + 1}: '{task['description']}' "
            f"(priority: {priority}, due: {due})"
        )
    lines.append(
        "\nBased on priority and due dates, advise the user on what to focus on first."
    )
    return "\n".join(lines)

def clear_all_tasks() -> str:
    count = len(tasks)
    tasks.clear()
    save_tasks()
    return f"Cleared all {count} task(s)."


# ---- Dispatcher: maps tool names → real functions ----

def run_tool(tool_name: str, tool_input: dict) -> str:
    try:
        if tool_name == "add_task":
            return add_task(**tool_input)
        if tool_name == "list_tasks":
            return list_tasks(**tool_input)
        if tool_name == "complete_task":
            return complete_task(**tool_input)
        if tool_name == "update_task":
            return update_task(**tool_input)
        if tool_name == "get_priorities":
            return get_priorities(**tool_input)
        if tool_name == "clear_all_tasks":
            return clear_all_tasks(**tool_input)
        print(f"⚠️  DEBUG: unknown tool_name='{tool_name}'")
        return f"Error: unknown tool '{tool_name}'"
    except Exception as e:
        print(f"⚠️  DEBUG: tool '{tool_name}' crashed: {type(e).__name__}: {e}")
        return f"Error running {tool_name}: {e}"


# ---- Tool schemas (what Claude sees) ----

TOOL_SCHEMAS = [
    {
        "name": "add_task",
        "description": "Add a new task to the user's to-do list. Use this whenever the user wants to remember something or note something to do. Capture a due date or priority ONLY if the user mentions one — don't invent them.",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "A short description of the task."
                },
                "due": {
                    "type": "string",
                    "description": "Optional. When the task is due, as the user expressed it (e.g. 'Friday', 'tomorrow', 'May 25'). Omit if not mentioned."
                },
                "priority": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Optional. Task priority. Only set if the user indicates urgency or importance. Omit if not mentioned."
                }
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
        "name": "update_task",
        "description": "Modify an existing task's description, due date, or priority by its number (1-based). Use this when the user wants to change a task they already created (e.g. 'make the coursework one high priority', 'change the milk due date to Saturday', 'rename task 2'). Only pass the fields the user wants to change. If you don't know the task number, call list_tasks first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_number": {
                    "type": "integer",
                    "description": "The task number to update (1-based, as shown to the user)."
                },
                "description": {
                    "type": "string",
                    "description": "Optional. New description text. Only include if the user wants to rename the task."
                },
                "due": {
                    "type": "string",
                    "description": "Optional. New due date as the user expressed it. Only include if changing the due date."
                },
                "priority": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Optional. New priority. Only include if changing priority."
                }
            },
            "required": ["task_number"]
        }
    },
    {
        "name": "clear_all_tasks",
        "description": "Delete ALL tasks from the list. Only use this when the user clearly wants to wipe everything (e.g. 'clear my list', 'start over'). Never use this for partial deletions.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "get_priorities",
        "description": "Analyze the user's pending tasks and recommend what to focus on first, based on priority levels and due dates. Use this when the user asks things like 'what should I do first?', 'what should I focus on?', 'help me prioritize', or 'what's most urgent?'.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
]