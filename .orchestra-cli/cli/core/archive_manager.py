"""Task archival and cleanup management."""

import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task, TaskStatus
from cli.core.repository import TaskRepository
from cli.core.config import OrchestratorConfig
from cli.utils.logger import logger


class ArchiveManager:
    """Manages automatic task archival and cleanup."""

    def __init__(
        self, repo: TaskRepository, config: Optional[OrchestratorConfig] = None
    ):
        self.repo = repo
        self.config = config or OrchestratorConfig.load()
        self.archive_dir = Path(self.config.archive.archive_dir)

    def get_archivable_tasks(self) -> List[Task]:
        """Find tasks eligible for archival based on age."""
        now = datetime.now()
        archivable = []

        for task in self.repo.load_all():
            if task.status == TaskStatus.COMPLETE:
                age = now - (task.completedAt or task.createdAt)
                if age.days >= self.config.archive.max_completed_age_days:
                    archivable.append(task)
            elif task.status in (TaskStatus.FAILED, TaskStatus.CANCELLED):
                age = now - (task.completedAt or task.createdAt)
                if age.days >= self.config.archive.max_failed_age_days:
                    archivable.append(task)

        return archivable

    def archive_task(self, task: Task) -> bool:
        """Move a task and its files to the archive directory."""
        try:
            self.archive_dir.mkdir(parents=True, exist_ok=True)

            # Archive task JSON
            archive_path = self.archive_dir / f"{task.taskId}.json"
            archive_path.write_text(task.model_dump_json(indent=2))

            # Archive plan and log files
            for src in [Path(task.planFile), Path(task.logFile)]:
                if src.exists():
                    dst = self.archive_dir / src.name
                    shutil.copy2(src, dst)

            # Delete original files
            self.repo.delete(task.taskId)
            logger.info(f"Archived task {task.taskId}")
            return True
        except Exception as e:
            logger.error(f"Failed to archive {task.taskId}: {e}")
            return False

    def run_archival(self) -> Tuple[int, int]:
        """Run archival process. Returns (archived_count, error_count)."""
        if not self.config.archive.enabled:
            return 0, 0

        tasks = self.get_archivable_tasks()
        archived = sum(1 for t in tasks if self.archive_task(t))
        errors = len(tasks) - archived
        return archived, errors

    def check_queue_size(self) -> bool:
        """Check if queue size exceeds limit. Returns True if OK."""
        current_size = len(self.repo.load_all())
        limit = self.config.archive.max_queue_size

        if current_size >= limit:
            logger.warning(
                f"Task queue size ({current_size}) exceeds limit ({limit}). "
                f"Consider running: python3 -m cli clean all"
            )
            return False
        return True

    def get_archive_stats(self) -> dict:
        """Get statistics about archived tasks."""
        if not self.archive_dir.exists():
            return {"total": 0, "size_mb": 0}

        archived_files = list(self.archive_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in archived_files)

        return {"total": len(archived_files), "size_mb": total_size / (1024 * 1024)}

