"""Task index for faster lookups in large queues."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task, TaskStatus
from cli.utils.logger import logger


class TaskIndex:
    """Maintains an index of tasks for fast queries."""

    def __init__(self, index_path: Path = None):
        self.path = index_path or Path(".orchestra/tasks/index.json")
        self.data = self._load()

    def _load(self) -> dict:
        """Load index from file."""
        if self.path.exists():
            try:
                with open(self.path) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load index: {e}")
        
        return {
            "by_status": {},
            "by_agent": {},
            "by_priority": {},
            "count": 0,
            "last_updated": None,
        }

    def _save(self):
        """Save index to file."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.data["last_updated"] = datetime.now().isoformat()
            with open(self.path, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def add(self, task: Task):
        """Add task to index."""
        task_id = task.taskId
        status = task.status.value
        agent = task.agent
        priority = task.priority

        # Add to status index
        if status not in self.data["by_status"]:
            self.data["by_status"][status] = []
        if task_id not in self.data["by_status"][status]:
            self.data["by_status"][status].append(task_id)

        # Add to agent index
        if agent not in self.data["by_agent"]:
            self.data["by_agent"][agent] = []
        if task_id not in self.data["by_agent"][agent]:
            self.data["by_agent"][agent].append(task_id)

        # Add to priority index
        priority_key = str(priority)
        if priority_key not in self.data["by_priority"]:
            self.data["by_priority"][priority_key] = []
        if task_id not in self.data["by_priority"][priority_key]:
            self.data["by_priority"][priority_key].append(task_id)

        self.data["count"] = self._count_unique_tasks()
        self._save()

    def remove(self, task_id: str):
        """Remove task from index."""
        # Remove from all indices
        for status_list in self.data["by_status"].values():
            if task_id in status_list:
                status_list.remove(task_id)

        for agent_list in self.data["by_agent"].values():
            if task_id in agent_list:
                agent_list.remove(task_id)

        for priority_list in self.data["by_priority"].values():
            if task_id in priority_list:
                priority_list.remove(task_id)

        self.data["count"] = self._count_unique_tasks()
        self._save()

    def update_status(self, task_id: str, old_status: str, new_status: str):
        """Update task status in index."""
        # Remove from old status
        if old_status in self.data["by_status"]:
            if task_id in self.data["by_status"][old_status]:
                self.data["by_status"][old_status].remove(task_id)

        # Add to new status
        if new_status not in self.data["by_status"]:
            self.data["by_status"][new_status] = []
        if task_id not in self.data["by_status"][new_status]:
            self.data["by_status"][new_status].append(task_id)

        self._save()

    def get_by_status(self, status: str) -> List[str]:
        """Get task IDs by status."""
        return self.data["by_status"].get(status, [])

    def get_by_agent(self, agent: str) -> List[str]:
        """Get task IDs by agent."""
        return self.data["by_agent"].get(agent, [])

    def get_by_priority(self, priority: int) -> List[str]:
        """Get task IDs by priority."""
        return self.data["by_priority"].get(str(priority), [])

    def rebuild(self, tasks: List[Task]):
        """Rebuild index from scratch."""
        self.data = {
            "by_status": {},
            "by_agent": {},
            "by_priority": {},
            "count": 0,
            "last_updated": None,
        }

        for task in tasks:
            self.add(task)

        logger.info(f"Rebuilt index with {len(tasks)} tasks")

    def _count_unique_tasks(self) -> int:
        """Count unique task IDs across all indices."""
        all_ids = set()
        for status_list in self.data["by_status"].values():
            all_ids.update(status_list)
        return len(all_ids)

