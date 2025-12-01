"""Start command implementation - creates new tasks."""

import sys
from pathlib import Path
from datetime import datetime

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task, TaskStatus
from cli.core.repository import TaskRepository
from cli.utils.time_utils import format_duration


def start_command(
    agent: str,
    prompt: str,
    max_retries: int = 3,
    auto_retry: bool = False,
    priority: int = 5,
    timeout: int = None,
):
    """
    Queue a new agent task.

    Args:
        agent: Agent name (e.g., 'coder')
        prompt: Task description/prompt
        max_retries: Maximum retry attempts
        auto_retry: Enable automatic retries
        priority: Task priority (1-10)
        timeout: Timeout in seconds (None for no timeout)
    """
    # Generate task ID
    task_id = f"task_{int(datetime.now().timestamp() * 1000)}"

    # Create task
    task = Task(
        taskId=task_id,
        status=TaskStatus.PENDING,
        agent=agent,
        prompt=prompt,
        planFile=f".gemini/agents/plans/{task_id}_plan.md",
        logFile=f".gemini/agents/logs/{task_id}.log",
        createdAt=datetime.now(),
        maxRetries=max_retries,
        autoRetry=auto_retry,
        priority=priority,
        timeout=timeout,
        timeoutWarning=60 if timeout else None,
    )

    # Save task
    repo = TaskRepository()
    repo.save(task)

    # Create plan file
    plan_path = Path(task.planFile)
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(f"# Task: {task_id}\n\n## Prompt\n{prompt}\n")

    # Report
    print(f"\033[92mTask {task_id} created for {agent}\033[0m")  # Green
    if max_retries != 3:
        print(f"  Max retries: {max_retries}")
    if auto_retry:
        print(f"  Auto-retry: enabled")
    if priority != 5:
        print(f"  Priority: {priority}")
    if timeout:
        print(f"  Timeout: {timeout}s ({format_duration(timeout)})")
