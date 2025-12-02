"""Clean command implementation - removes old task files."""

import sys
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import TaskStatus
from cli.core.repository import TaskRepository


def clean_command(filter_type: str = "completed", force: bool = False):
    """
    Remove old task files based on filter criteria.

    Args:
        filter_type: Filter type (completed, failed, cancelled, all, or task_id)
        force: Skip confirmation prompt
    """
    repo = TaskRepository()

    # 1. Determine filter and find matching tasks
    matching_tasks = []

    if filter_type.startswith("task_"):
        # Specific task ID
        task = repo.get_task(filter_type)
        if not task:
            print(f"Error: Task {filter_type} not found.")
            sys.exit(1)
        matching_tasks = [task]
    else:
        # Load all tasks
        all_tasks = repo.list_tasks()

        # Filter based on type
        if filter_type == "completed":
            matching_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETE]
        elif filter_type == "failed":
            matching_tasks = [t for t in all_tasks if t.status == TaskStatus.FAILED]
        elif filter_type == "cancelled":
            matching_tasks = [t for t in all_tasks if t.status == TaskStatus.CANCELLED]
        elif filter_type == "all":
            matching_tasks = [
                t
                for t in all_tasks
                if t.status
                in (TaskStatus.COMPLETE, TaskStatus.FAILED, TaskStatus.CANCELLED)
            ]
        else:
            print(f"Error: Invalid filter type '{filter_type}'.")
            print("Valid filters: completed, failed, cancelled, all, task_<id>")
            sys.exit(1)

    # 2. Safety check - never delete running or pending
    matching_tasks = [
        t
        for t in matching_tasks
        if t.status not in (TaskStatus.RUNNING, TaskStatus.PENDING)
    ]

    if not matching_tasks:
        print(f"No tasks found matching filter: {filter_type}")
        return

    # 3. Confirmation for large deletions
    if len(matching_tasks) > 10 and not force:
        print(f"Found {len(matching_tasks)} tasks to delete:")
        for task in matching_tasks[:10]:
            print(f"  - {task.taskId} ({task.status.value})")
        if len(matching_tasks) > 10:
            print(f"  ... and {len(matching_tasks) - 10} more")
        response = input("\nProceed with deletion? (y/N): ")
        if response.lower() != "y":
            print("Cancelled.")
            return

    # 4. Delete task artifacts
    deleted_count = 0
    deleted_ids = []

    for task in matching_tasks:
        task_id = task.taskId

        # Delete JSON file
        json_path = repo.tasks_dir / f"{task_id}.json"
        if json_path.exists():
            json_path.unlink()

        # Delete plan file
        plan_path = Path(task.planFile)
        if plan_path.exists():
            plan_path.unlink()

        # Delete log file
        log_path = Path(task.logFile)
        if log_path.exists():
            log_path.unlink()

        # Delete sentinel files
        for sentinel in [".done", ".error", ".cancelled", ".timeout"]:
            sentinel_path = repo.tasks_dir / f"{task_id}{sentinel}"
            if sentinel_path.exists():
                sentinel_path.unlink()

        deleted_count += 1
        deleted_ids.append(task_id)

    # 5. Report
    if deleted_count == 1:
        print(f"Cleaned up 1 task: {deleted_ids[0]}")
    else:
        ids_str = ", ".join(deleted_ids[:5])
        if len(deleted_ids) > 5:
            ids_str += f", ... and {len(deleted_ids) - 5} more"
        print(f"Cleaned up {deleted_count} {filter_type} tasks: {ids_str}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clean up task files")
    parser.add_argument(
        "filter",
        nargs="?",
        default="completed",
        help="Filter type: completed, failed, cancelled, all, or task_id",
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="Skip confirmation prompt"
    )

    args = parser.parse_args()
    clean_command(args.filter, args.force)
