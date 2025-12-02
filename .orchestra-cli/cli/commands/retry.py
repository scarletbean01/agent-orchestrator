"""Retry command implementation - retries failed tasks."""

import sys
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task, TaskStatus, RetryHistoryEntry
from cli.core.repository import TaskRepository
from cli.core.retry_manager import RetryManager


def retry_command(
    task_id: str,
    max_retries: int = None,
    auto_retry: bool = False,
):
    """
    Retry a failed task with proper tracking and auto-retry support.

    Args:
        task_id: ID of the failed task to retry
        max_retries: Override max retries (None to use original)
        auto_retry: Enable automatic retries for new task
    """
    repo = TaskRepository()

    # 1. Validate task exists and is failed
    original = repo.get_task(task_id)
    if not original:
        print(f"Error: Task {task_id} not found.")
        sys.exit(1)

    if original.status != TaskStatus.FAILED:
        print(
            f"Error: Task {task_id} is not in failed state (current: {original.status.value})."
        )
        print("Only failed tasks can be retried.")
        sys.exit(1)

    # 2. Use RetryManager to create retry task
    retry_manager = RetryManager(repo)
    new_task = retry_manager.create_retry_task(
        original, auto_retry=auto_retry, max_retries_override=max_retries
    )

    if not new_task:
        # RetryManager handles checking limits and logging reasons
        # But we want to explicitly tell the user why if it failed due to limits
        effective_max = max_retries if max_retries is not None else original.maxRetries
        if original.retryCount >= effective_max:
            print(
                f"Error: Task {task_id} has reached max retries ({original.retryCount}/{effective_max})."
            )
            print("Cannot retry.")
            sys.exit(1)
        else:
            print("Error: Failed to create retry task.")
            sys.exit(1)

    # 3. Report
    print(
        f"Task {new_task.taskId} created as retry for {task_id} (attempt {new_task.retryCount}/{new_task.maxRetries})"
    )
    if auto_retry:
        print("Auto-retry enabled - will automatically retry on future failures")
    print("Use /agent:run or /agent:run-parallel to execute the retry")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Retry a failed task")
    parser.add_argument("task_id", help="Task ID to retry")
    parser.add_argument(
        "--max-retries",
        type=int,
        default=None,
        help="Override max retries (default: use original)",
    )
    parser.add_argument(
        "--auto-retry", action="store_true", help="Enable auto-retry for new task"
    )

    args = parser.parse_args()
    retry_command(args.task_id, args.max_retries, args.auto_retry)
