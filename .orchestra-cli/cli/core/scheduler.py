"""Task scheduling and queue management."""

import sys
from pathlib import Path
from typing import List, Optional

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task, TaskStatus
from cli.core.repository import TaskRepository
from cli.core.dependency_resolver import DependencyResolver


class Scheduler:
    """Manages task queue and scheduling."""

    def __init__(self, repo: TaskRepository):
        self.repo = repo
        self.resolver = DependencyResolver(repo)

    def get_next_pending(self) -> Optional[Task]:
        """
        Get the next pending task to execute (priority + dependencies).

        Returns None if no pending tasks with satisfied dependencies.
        """
        # Get tasks with satisfied dependencies
        ready_tasks = self.resolver.get_ready_tasks()
        if not ready_tasks:
            return None

        # Sort by priority (higher = more important), then by createdAt (oldest first)
        ready_tasks.sort(key=lambda t: (-t.priority, t.createdAt))
        return ready_tasks[0]

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
            List of pending tasks with satisfied dependencies (sorted by priority)
        """
        # Get tasks with satisfied dependencies
        ready_tasks = self.resolver.get_ready_tasks()
        # Sort by priority (higher = more important), then by createdAt (oldest first)
        ready_tasks.sort(key=lambda t: (-t.priority, t.createdAt))
        return ready_tasks[:limit]
