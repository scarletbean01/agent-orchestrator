from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from cli.core.models import Task, TaskStatus, RetryHistoryEntry
from cli.core.repository import TaskRepository
from cli.utils.logger import logger


class RetryManager:
    """Manages retry logic for failed tasks."""

    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def create_retry_task(
        self,
        original_task: Task,
        auto_retry: bool,
        max_retries_override: Optional[int] = None,
    ) -> Optional[Task]:
        """
        Creates a new task as a retry for the original task.
        Returns the new retry task if created, None otherwise.
        """
        new_retry_count = original_task.retryCount + 1
        effective_max_retries = (
            max_retries_override
            if max_retries_override is not None
            else original_task.maxRetries
        )

        if new_retry_count > effective_max_retries:
            logger.info(
                f"Task {original_task.taskId} reached max retries ({original_task.retryCount}/{effective_max_retries}). Skipping retry."
            )
            return None

        new_task_id = f"task_{int(datetime.now().timestamp() * 1000)}"
        parent_id = (
            original_task.parentTaskId
            if original_task.parentTaskId
            else original_task.taskId
        )

        retry_history = (
            list(original_task.retryHistory) if original_task.retryHistory else []
        )
        retry_history.append(
            RetryHistoryEntry(
                attempt=new_retry_count,
                timestamp=datetime.now(),
                error=original_task.errorMessage or "Unknown error",
                retriedFrom=original_task.taskId,
            )
        )

        # Use repository's directory paths to ensure consistency
        plan_file = str(self.repo.plans_dir / f"{new_task_id}_plan.md")
        log_file = str(self.repo.logs_dir / f"{new_task_id}.log")

        retry_task = Task(
            taskId=new_task_id,
            status=TaskStatus.PENDING,
            agent=original_task.agent,
            prompt=original_task.prompt,
            planFile=plan_file,
            logFile=log_file,
            createdAt=datetime.now(),
            retryCount=new_retry_count,
            maxRetries=effective_max_retries,
            autoRetry=auto_retry,
            parentTaskId=parent_id,
            retryHistory=retry_history,
            priority=original_task.priority,
            timeout=original_task.timeout,
            timeoutWarning=original_task.timeoutWarning,
        )

        self.repo.save(retry_task)

        # Create plan file
        plan_path = Path(retry_task.planFile)
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_content = f"# Retry Attempt {new_retry_count}/{effective_max_retries}\n\n"
        plan_content += f"**Original Task:** {original_task.taskId}\n"
        plan_content += (
            f"**Previous Error:** {original_task.errorMessage or 'Unknown error'}\n\n"
        )
        plan_content += "## Task Prompt\n"
        plan_content += f"{original_task.prompt}\n\n"
        plan_content += "## Retry Strategy\n"
        plan_content += (
            f"This is retry attempt {new_retry_count} of {effective_max_retries}.\n"
        )
        plan_content += f"Auto-retry: {'enabled' if auto_retry else 'disabled'}\n"

        plan_path.write_text(plan_content)

        # Update original task
        original_task.retriedBy = new_task_id
        original_task.retriedAt = datetime.now()
        self.repo.save(original_task)

        logger.info(
            f"Task {new_task_id} created as retry for {original_task.taskId} (attempt {new_retry_count}/{effective_max_retries})"
        )
        return retry_task

    def is_retry_due(self, task: Task) -> bool:
        """
        Checks if a failed task is due for an automatic retry based on exponential backoff.
        """
        if not task.autoRetry or task.status != TaskStatus.FAILED:
            return False

        if task.retryCount >= task.maxRetries:
            return False

        # Exponential backoff: 2^retryCount seconds
        backoff_seconds = 2**task.retryCount

        # Determine the base time for backoff calculation
        # If retriedAt is set, it means a previous retry occurred, but we are checking if *another* one is due?
        # No, is_retry_due checks if the *current* failure (task) should trigger a *new* retry task.
        # So we look at when this task completed (failed).

        base_time = task.completedAt or datetime.now()
        wait_until = base_time + timedelta(seconds=backoff_seconds)

        return datetime.now() >= wait_until
