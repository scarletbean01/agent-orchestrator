"""Cancel command implementation."""

import sys
from datetime import datetime
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.repository import TaskRepository
from cli.core.models import TaskStatus
from cli.utils.process import kill_process


def cancel_command(task_id: str):
    """
    Cancel a running or pending task.

    Args:
        task_id: Task ID to cancel
    """
    repo = TaskRepository()
    task = repo.load(task_id)

    if not task:
        print(f"\033[91mError: Task {task_id} not found\033[0m")  # Red
        return

    if task.status == TaskStatus.PENDING:
        task.status = TaskStatus.CANCELLED
        task.completedAt = datetime.now()
        repo.save(task)
        print(f"\033[93mTask {task_id} cancelled (was pending)\033[0m")  # Yellow

    elif task.status == TaskStatus.RUNNING:
        if task.pid:
            success = kill_process(task.pid)
            if success:
                print(f"\033[93mProcess {task.pid} terminated\033[0m")  # Yellow

        task.status = TaskStatus.CANCELLED
        task.completedAt = datetime.now()
        repo.save(task)

        # Create sentinel
        repo.write_sentinel_file(task_id, "cancelled")

        print(f"\033[92mTask {task_id} cancelled\033[0m")  # Green

    else:
        print(
            f"\033[93mTask {task_id} is {task.status.value} (cannot cancel)\033[0m"
        )  # Yellow
