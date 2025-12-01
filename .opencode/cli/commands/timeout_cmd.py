"""Timeout command implementation - manages task timeouts."""

import sys
from pathlib import Path
from datetime import datetime

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import TaskStatus
from cli.core.repository import TaskRepository
from cli.utils.process import kill_process
from cli.utils.time_utils import format_duration


def timeout_immediate(task_id: str):
    """Immediately terminate a task as timed out."""
    repo = TaskRepository()

    # Validate task
    task = repo.get_task(task_id)
    if not task:
        print(f"Error: Task {task_id} not found.")
        sys.exit(1)

    if task.status != TaskStatus.RUNNING:
        print(
            f"Error: Task {task_id} is not running (current status: {task.status.value})."
        )
        sys.exit(1)

    if not task.pid:
        print(f"Error: Task {task_id} has no PID recorded.")
        sys.exit(1)

    # Terminate process
    print(f"Terminating task {task_id} (PID: {task.pid})...")
    if kill_process(task.pid):
        print(f"Task {task_id} terminated successfully.")
    else:
        print(f"Warning: Failed to terminate PID {task.pid} (may already be dead).")

    # Create .timeout sentinel file
    timeout_file = repo.tasks_dir / f"{task_id}.timeout"
    timeout_file.write_text(
        f'{{"timeout": "manual", "timestamp": "{datetime.now().isoformat()}"}}'
    )

    print(
        "Task will be marked as timed out on next /agent:status or 'python3 -m cli status' check."
    )


def timeout_list():
    """List all tasks with timeouts."""
    repo = TaskRepository()
    all_tasks = repo.list_tasks()

    # Filter tasks with timeouts
    timeout_tasks = [t for t in all_tasks if t.timeout is not None]

    if not timeout_tasks:
        print("No tasks with timeouts found.")
        return

    # Build table
    print("\n| ID         | Status | Timeout | Elapsed | Remaining | State |")
    print("|------------|--------|---------|---------|-----------|-------|")

    for task in timeout_tasks:
        task_id = task.taskId[:12] + "..." if len(task.taskId) > 12 else task.taskId

        # Status icon
        status_icon = {
            TaskStatus.COMPLETE: "✓",
            TaskStatus.FAILED: "✗",
            TaskStatus.RUNNING: "⏱",
            TaskStatus.PENDING: "⏸",
            TaskStatus.CANCELLED: "⊗",
        }.get(task.status, "?")

        # Timeout limit
        timeout_str = format_duration(task.timeout)

        # Elapsed and remaining (only for running tasks)
        elapsed_str = ""
        remaining_str = ""
        state_str = status_icon

        if task.status == TaskStatus.RUNNING and task.startedAt:
            elapsed = (datetime.now() - task.startedAt).total_seconds()
            elapsed_str = format_duration(int(elapsed))

            remaining = task.timeout - elapsed
            if remaining > 0:
                remaining_str = format_duration(int(remaining))
                # Warning states
                if remaining < 60:
                    state_str = "⏱⚠"  # Critical
                elif remaining < task.timeout * 0.2:
                    state_str = "⚠"  # Warning
            else:
                remaining_str = "OVERDUE"
                state_str = "⏱⚠"
        elif task.status == TaskStatus.FAILED and "timeout" in (
            task.errorMessage or ""
        ):
            state_str = "✗⏱"

        print(
            f"| {task_id:<10} | {status_icon:<6} | {timeout_str:<7} | {elapsed_str:<7} | {remaining_str:<9} | {state_str:<5} |"
        )

    # Summary
    total = len(timeout_tasks)
    running = sum(1 for t in timeout_tasks if t.status == TaskStatus.RUNNING)
    timed_out = sum(
        1
        for t in timeout_tasks
        if t.status == TaskStatus.FAILED and "timeout" in (t.errorMessage or "")
    )

    print(
        f"\nTotal with timeouts: {total} | Running: {running} | Timed out: {timed_out}"
    )


def timeout_extend(task_id: str, seconds: int):
    """Extend timeout for a task (metadata only - cannot extend running process)."""
    repo = TaskRepository()

    # Validate task
    task = repo.get_task(task_id)
    if not task:
        print(f"Error: Task {task_id} not found.")
        sys.exit(1)

    if task.status == TaskStatus.RUNNING:
        print(f"⚠️  WARNING: Task {task_id} is currently running.")
        print(
            "Cannot dynamically extend timeout for a running process with GNU timeout."
        )
        print("\nTo extend timeout for a running task:")
        print(f"  1. Cancel the task: python3 -m cli cancel {task_id}")
        print(
            f'  2. Create new task with extended timeout: python3 -m cli start {task.agent} "{task.prompt}" --timeout {(task.timeout or 0) + seconds}'
        )
        print("  3. Run the new task: python3 -m cli run")
        sys.exit(1)

    # Update metadata (for pending tasks or documentation)
    old_timeout = task.timeout or 0
    new_timeout = old_timeout + seconds
    task.timeout = new_timeout
    repo.save_task(task)

    print(
        f"Updated timeout for task {task_id}: {format_duration(old_timeout)} → {format_duration(new_timeout)}"
    )
    if task.status == TaskStatus.PENDING:
        print("(Task is pending - new timeout will apply when it runs)")


def timeout_command(subcommand: str, *args):
    """
    Manage task timeouts.

    Subcommands:
        <task_id>: Immediately terminate a task as timed out
        list: Show all tasks with timeouts
        extend <task_id> <seconds>: Extend timeout (metadata only)
    """
    if subcommand == "list":
        timeout_list()
    elif subcommand == "extend":
        if len(args) < 2:
            print("Error: extend requires <task_id> <seconds>")
            sys.exit(1)
        task_id = args[0]
        try:
            seconds = int(args[1])
        except ValueError:
            print(f"Error: Invalid seconds value: {args[1]}")
            sys.exit(1)
        timeout_extend(task_id, seconds)
    else:
        # Treat as task_id for immediate timeout
        timeout_immediate(subcommand)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage task timeouts")
    parser.add_argument(
        "subcommand", help="Subcommand: <task_id>, list, or extend <task_id> <seconds>"
    )
    parser.add_argument("args", nargs="*", help="Additional arguments")

    args = parser.parse_args()
    timeout_command(args.subcommand, *args.args)
