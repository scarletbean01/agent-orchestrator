"""Task scheduling and queue management."""

import sys
from pathlib import Path
from typing import List, Optional

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task, TaskStatus
from cli.core.repository import TaskRepository


class Scheduler:
    """Manages task queue and scheduling."""

    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def get_next_pending(self) -> Optional[Task]:
        """
        Get the next pending task to execute (FIFO with priority).

        Returns None if no pending tasks.
        """
        tasks = self.repo.load_all()
        pending = [t for t in tasks if t.status == TaskStatus.PENDING]
        if not pending:
            return None

        # Sort by createdAt (oldest first), then by priority (higher = more important)
        pending.sort(key=lambda t: (t.createdAt, -t.priority))
        return pending[0]

    def get_running_count(self) -> int:
        """Count currently running tasks."""
        tasks = self.repo.load_all()
        return sum(1 for t in tasks if t.status == TaskStatus.RUNNING)

    def get_pending_tasks(self, limit: int) -> List[Task]:
        """
        Get multiple pending tasks for parallel execution.

        Args:
            limit: Maximum number of tasks to return

        Returns:
            List of pending tasks (oldest first, sorted by priority)
        """
        tasks = self.repo.load_all()
        pending = [t for t in tasks if t.status == TaskStatus.PENDING]
        pending.sort(key=lambda t: (t.createdAt, -t.priority))
        return pending[:limit]
