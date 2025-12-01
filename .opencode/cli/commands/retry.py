"""Retry command implementation - retries failed tasks."""

import sys
from pathlib import Path
from datetime import datetime

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task, TaskStatus, RetryHistoryEntry
from cli.core.repository import TaskRepository


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

    # 2. Extract task info
    new_retry_count = original.retryCount + 1
    effective_max_retries = (
        max_retries if max_retries is not None else original.maxRetries
    )

    # 3. Check retry limit
    if new_retry_count > effective_max_retries:
        print(
            f"Error: Task {task_id} has reached max retries ({original.retryCount}/{effective_max_retries})."
        )
        print("Cannot retry.")
        sys.exit(1)

    # 4. Create retry task
    new_task_id = f"task_{int(datetime.now().timestamp() * 1000)}"
    parent_id = original.parentTaskId if original.parentTaskId else task_id

    # Build retry history
    retry_history = list(original.retryHistory) if original.retryHistory else []
    retry_history.append(
        RetryHistoryEntry(
            attempt=new_retry_count,
            timestamp=datetime.now(),
            error=original.errorMessage or "Unknown error",
            retriedFrom=task_id,
        )
    )

    # Create new task
    retry_task = Task(
        taskId=new_task_id,
        status=TaskStatus.PENDING,
        agent=original.agent,
        prompt=original.prompt,
        planFile=f".gemini/agents/plans/{new_task_id}_plan.md",
        logFile=f".gemini/agents/logs/{new_task_id}.log",
        createdAt=datetime.now(),
        retryCount=new_retry_count,
        maxRetries=effective_max_retries,
        autoRetry=auto_retry,
        parentTaskId=parent_id,
        retryHistory=retry_history,
        priority=original.priority,
        timeout=original.timeout,
        timeoutWarning=original.timeoutWarning,
    )

    # Save retry task
    repo.save_task(retry_task)

    # 5. Create plan file
    plan_path = Path(retry_task.planFile)
    plan_path.parent.mkdir(parents=True, exist_ok=True)

    plan_content = f"""# Retry Attempt {new_retry_count}/{effective_max_retries}

**Original Task:** {task_id}
**Previous Error:** {original.errorMessage or "Unknown error"}

## Task Prompt
{original.prompt}

## Retry Strategy
This is retry attempt {new_retry_count} of {effective_max_retries}.
Auto-retry: {"enabled" if auto_retry else "disabled"}
"""

    plan_path.write_text(plan_content)

    # 6. Update original task
    original.retriedBy = new_task_id
    original.retriedAt = datetime.now()
    repo.save_task(original)

    # 7. Report
    print(
        f"Task {new_task_id} created as retry for {task_id} (attempt {new_retry_count}/{effective_max_retries})"
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
