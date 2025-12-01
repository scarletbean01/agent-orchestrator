"""State reconciliation for tasks based on sentinel files and process health."""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from .models import Task, TaskStatus
from .repository import TaskRepository
from ..utils.process import is_process_alive, get_pid_from_file


class Reconciler:
    """Reconciles task status based on sentinel files and process state."""

    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def reconcile_task(self, task: Task) -> bool:
        """
        Update task status based on sentinel files and process health.

        Returns True if status changed.
        """
        if task.status != TaskStatus.RUNNING:
            return False

        sentinels = self.repo.get_sentinel_files(task.taskId)
        changed = False

        # Check completion sentinel
        if sentinels["done"]:
            task.status = TaskStatus.COMPLETE
            task.completedAt = datetime.now()
            self._cleanup_sentinel(task.taskId, "done")
            self._cleanup_sentinel(task.taskId, "exitcode")
            self._cleanup_sentinel(task.taskId, "pid")
            changed = True

        # Check error sentinel
        elif sentinels["error"]:
            task.status = TaskStatus.FAILED
            task.errorMessage = self._read_error_sentinel(task.taskId)
            task.completedAt = datetime.now()
            self._cleanup_sentinel(task.taskId, "error")
            self._cleanup_sentinel(task.taskId, "exitcode")
            self._cleanup_sentinel(task.taskId, "pid")
            changed = True

        # Check cancellation sentinel
        elif sentinels["cancelled"]:
            task.status = TaskStatus.CANCELLED
            task.completedAt = datetime.now()
            self._cleanup_sentinel(task.taskId, "cancelled")
            self._cleanup_sentinel(task.taskId, "exitcode")
            self._cleanup_sentinel(task.taskId, "pid")
            changed = True

        # Check timeout sentinel
        elif sentinels["timeout"]:
            task.status = TaskStatus.FAILED
            timeout_info = self._read_timeout_sentinel(task.taskId)
            task.errorMessage = (
                f"Task timed out after {timeout_info.get('timeout', '?')} seconds"
            )
            task.timedOutAt = self._parse_timestamp(timeout_info.get("timestamp"))
            task.completedAt = task.timedOutAt or datetime.now()
            self._cleanup_sentinel(task.taskId, "timeout")
            self._cleanup_sentinel(task.taskId, "exitcode")
            self._cleanup_sentinel(task.taskId, "pid")
            changed = True

        # Check process health
        elif task.pid:
            pid_file = (
                self.repo.tasks_dir / f"{task.taskId}.pid" if sentinels["pid"] else None
            )
            if not is_process_alive(task.pid, pid_file):
                # Process died - check exit code
                exitcode = self._read_exitcode(task.taskId)
                if exitcode == 124:
                    task.status = TaskStatus.FAILED
                    task.errorMessage = "Task timed out (exit code 124)"
                    task.timedOutAt = datetime.now()
                elif exitcode is not None and exitcode != 0:
                    task.status = TaskStatus.FAILED
                    task.errorMessage = f"Process exited with code {exitcode}"
                else:
                    task.status = TaskStatus.FAILED
                    task.errorMessage = "Process terminated unexpectedly"
                task.completedAt = datetime.now()
                self._cleanup_sentinel(task.taskId, "exitcode")
                self._cleanup_sentinel(task.taskId, "pid")
                changed = True

        if changed:
            self.repo.save(task)

        return changed

    def reconcile_all(self) -> int:
        """
        Reconcile all running tasks.

        Returns count of tasks that changed status.
        """
        tasks = self.repo.load_all()
        changed_count = 0
        for task in tasks:
            if self.reconcile_task(task):
                changed_count += 1
        return changed_count

    def _read_error_sentinel(self, task_id: str) -> str:
        """Read error message from .error sentinel file."""
        content = self.repo.read_sentinel_file(task_id, "error")
        if not content:
            return "Unknown error"

        try:
            data = json.loads(content)
            return data.get("error", "Unknown error")
        except:
            return content.strip() or "Unknown error"

    def _read_timeout_sentinel(self, task_id: str) -> dict:
        """Read timeout info from .timeout sentinel file."""
        content = self.repo.read_sentinel_file(task_id, "timeout")
        if not content:
            return {"timeout": None, "timestamp": datetime.now().isoformat()}

        try:
            return json.loads(content)
        except:
            return {"timeout": None, "timestamp": datetime.now().isoformat()}

    def _read_exitcode(self, task_id: str) -> Optional[int]:
        """Read exit code from .exitcode file."""
        content = self.repo.read_sentinel_file(task_id, "exitcode")
        if not content:
            return None

        try:
            return int(content.strip())
        except:
            return None

    def _cleanup_sentinel(self, task_id: str, suffix: str):
        """Delete a sentinel file."""
        self.repo.delete_sentinel_file(task_id, suffix)

    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO timestamp string."""
        if not timestamp_str:
            return None

        try:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except:
            return None
