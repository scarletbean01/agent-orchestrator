"""Repository pattern for task CRUD operations."""

import json
from pathlib import Path
from typing import List, Optional, Dict

from .models import Task
from ..utils.paths import TASKS_DIR, PLANS_DIR, LOGS_DIR


class TaskRepository:
    """Repository for managing task persistence."""

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize repository.

        Args:
            base_path: Optional custom base path (for testing)
        """
        if base_path:
            self.tasks_dir = base_path / "tasks"
            self.plans_dir = base_path / "plans"
            self.logs_dir = base_path / "logs"
        else:
            self.tasks_dir = TASKS_DIR
            self.plans_dir = PLANS_DIR
            self.logs_dir = LOGS_DIR

        self._ensure_dirs()

    def _ensure_dirs(self):
        """Create directories if they don't exist."""
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def save(self, task: Task) -> None:
        """
        Save task to JSON file atomically.

        Uses atomic write pattern: write to temp file, then rename.
        This prevents corruption if the process is interrupted.
        """
        import platform

        json_path = self.tasks_dir / f"{task.taskId}.json"
        temp_path = json_path.with_suffix(".tmp")

        # Write to temp file
        with open(temp_path, "w") as f:
            # Use model_dump_json with custom serialization
            json_data = task.model_dump(mode="json")
            # Convert datetime objects to ISO format strings
            json_str = json.dumps(json_data, indent=2, default=str)
            f.write(json_str)

        # Atomic rename (Windows requires removing target first)
        if platform.system() == "Windows" and json_path.exists():
            json_path.unlink()
        temp_path.rename(json_path)

    def load(self, task_id: str) -> Optional[Task]:
        """
        Load task from JSON file.

        Returns None if task doesn't exist or cannot be loaded.
        """
        json_path = self.tasks_dir / f"{task_id}.json"
        if not json_path.exists():
            return None

        try:
            with open(json_path) as f:
                return Task.model_validate_json(f.read())
        except Exception as e:
            # Log error but don't crash
            print(f"Warning: Failed to load {json_path}: {e}")
            return None

    def load_all(self) -> List[Task]:
        """
        Load all tasks, sorted by creation time (oldest first).

        Skips tasks that cannot be loaded (with warning).
        """
        tasks = []
        for json_file in sorted(self.tasks_dir.glob("*.json")):
            try:
                with open(json_file) as f:
                    task = Task.model_validate_json(f.read())
                    tasks.append(task)
            except Exception as e:
                print(f"Warning: Failed to load {json_file}: {e}")

        # Sort by creation time
        tasks.sort(key=lambda t: t.createdAt)
        return tasks

    def delete(self, task_id: str) -> bool:
        """
        Delete all files related to a task.

        Returns True if any files were deleted.
        """
        deleted = False

        # JSON file
        json_file = self.tasks_dir / f"{task_id}.json"
        if json_file.exists():
            json_file.unlink()
            deleted = True

        # Plan file
        plan_file = self.plans_dir / f"{task_id}_plan.md"
        if plan_file.exists():
            plan_file.unlink()
            deleted = True

        # Log file
        log_file = self.logs_dir / f"{task_id}.log"
        if log_file.exists():
            log_file.unlink()
            deleted = True

        # Sentinel files
        for suffix in [
            ".done",
            ".error",
            ".cancelled",
            ".timeout",
            ".exitcode",
            ".pid",
        ]:
            sentinel_file = self.tasks_dir / f"{task_id}{suffix}"
            if sentinel_file.exists():
                sentinel_file.unlink()
                deleted = True

        return deleted

    def get_sentinel_files(self, task_id: str) -> Dict[str, bool]:
        """
        Check which sentinel files exist for a task.

        Returns dict mapping sentinel type to existence boolean.
        """
        return {
            "done": (self.tasks_dir / f"{task_id}.done").exists(),
            "error": (self.tasks_dir / f"{task_id}.error").exists(),
            "cancelled": (self.tasks_dir / f"{task_id}.cancelled").exists(),
            "timeout": (self.tasks_dir / f"{task_id}.timeout").exists(),
            "exitcode": (self.tasks_dir / f"{task_id}.exitcode").exists(),
            "pid": (self.tasks_dir / f"{task_id}.pid").exists(),
        }

    def read_sentinel_file(self, task_id: str, sentinel_type: str) -> Optional[str]:
        """Read contents of a sentinel file."""
        sentinel_file = self.tasks_dir / f"{task_id}.{sentinel_type}"
        if not sentinel_file.exists():
            return None

        try:
            return sentinel_file.read_text()
        except Exception:
            return None

    def write_sentinel_file(self, task_id: str, sentinel_type: str, content: str = ""):
        """Write a sentinel file."""
        sentinel_file = self.tasks_dir / f"{task_id}.{sentinel_type}"
        sentinel_file.write_text(content)

    def delete_sentinel_file(self, task_id: str, sentinel_type: str):
        """Delete a sentinel file if it exists."""
        sentinel_file = self.tasks_dir / f"{task_id}.{sentinel_type}"
        sentinel_file.unlink(missing_ok=True)

    # Convenience aliases for cleaner command code
    def get_task(self, task_id: str) -> Optional[Task]:
        """Alias for load()."""
        return self.load(task_id)

    def save_task(self, task: Task) -> None:
        """Alias for save()."""
        return self.save(task)

    def list_tasks(self) -> List[Task]:
        """Alias for load_all()."""
        return self.load_all()
