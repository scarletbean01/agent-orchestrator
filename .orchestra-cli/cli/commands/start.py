"""Start command implementation - creates new tasks."""

import sys
from datetime import datetime
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task, TaskStatus
from cli.core.repository import TaskRepository
from cli.core.dependency_resolver import DependencyResolver
from cli.utils.time_utils import format_duration
from typing import Optional, List


def start_command(
    agent: str,
    prompt: str,
    max_retries: int = 3,
    auto_retry: bool = False,
    priority: int = 5,
    timeout: int = None,
    depends_on: Optional[List[str]] = None,
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
        depends_on: List of task IDs this task depends on
    """
    repo = TaskRepository()

    # Validate dependencies
    if depends_on:
        resolver = DependencyResolver(repo)
        for dep_id in depends_on:
            dep_task = repo.load(dep_id)
            if not dep_task:
                print(f"\033[91mError: Dependency task {dep_id} not found\033[0m")
                return

        # Generate temporary task ID for cycle detection
        temp_task_id = f"task_{int(datetime.now().timestamp() * 1000)}"
        valid, message = resolver.validate_new_dependency(temp_task_id, depends_on)
        if not valid:
            print(f"\033[91mError: {message}\033[0m")
            return

    # Generate task ID
    task_id = f"task_{int(datetime.now().timestamp() * 1000)}"

    # Create task
    task = Task(
        taskId=task_id,
        status=TaskStatus.PENDING,
        agent=agent,
        prompt=prompt,
        planFile=f".orchestra/plans/{task_id}_plan.md",
        logFile=f".orchestra/logs/{task_id}.log",
        createdAt=datetime.now(),
        maxRetries=max_retries,
        autoRetry=auto_retry,
        priority=priority,
        timeout=timeout,
        timeoutWarning=60 if timeout else None,
        dependsOn=depends_on or [],
    )

    # Save task
    repo.save(task)

    # Create plan file
    plan_path = Path(task.planFile)
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_content = f"# Task: {task_id}\n\n## Prompt\n{prompt}\n"
    if depends_on:
        plan_content += f"\n## Dependencies\n"
        for dep_id in depends_on:
            plan_content += f"- {dep_id}\n"
    plan_path.write_text(plan_content)

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
    if depends_on:
        print(f"  Dependencies: {', '.join(depends_on)}")
