"""Tests for task repository."""

import sys
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.repository import TaskRepository
from cli.core.models import TaskStatus


class TestRepository:
    """Test cases for TaskRepository."""

    def test_save_and_load(self, repo, sample_task):
        """Should save and load a task."""
        repo.save(sample_task)
        loaded = repo.load(sample_task.taskId)
        assert loaded is not None
        assert loaded.taskId == sample_task.taskId
        assert loaded.status == sample_task.status

    def test_load_nonexistent(self, repo):
        """Should return None for nonexistent task."""
        loaded = repo.load("nonexistent_task")
        assert loaded is None

    def test_load_all(self, repo, sample_task, completed_task):
        """Should load all tasks."""
        repo.save(sample_task)
        repo.save(completed_task)
        tasks = repo.load_all()
        assert len(tasks) == 2
        task_ids = [t.taskId for t in tasks]
        assert sample_task.taskId in task_ids
        assert completed_task.taskId in task_ids

    def test_load_all_sorted(self, repo, sample_task, completed_task):
        """Should load tasks sorted by creation time."""
        # Save in reverse order
        repo.save(completed_task)
        repo.save(sample_task)
        
        tasks = repo.load_all()
        # Should be sorted by createdAt (oldest first)
        assert len(tasks) == 2

    def test_delete(self, repo, sample_task):
        """Should delete a task and its files."""
        repo.save(sample_task)
        
        # Create plan and log files
        plan_path = Path(sample_task.planFile)
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text("Test plan")
        
        log_path = Path(sample_task.logFile)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("Test log")
        
        # Delete task
        repo.delete(sample_task.taskId)
        
        # Verify deletion
        assert repo.load(sample_task.taskId) is None
        assert not plan_path.exists()
        assert not log_path.exists()

    def test_list_tasks(self, repo, sample_task, completed_task):
        """Should list all tasks."""
        repo.save(sample_task)
        repo.save(completed_task)
        tasks = repo.list_tasks()
        assert len(tasks) == 2

    def test_sentinel_files(self, repo, sample_task):
        """Should manage sentinel files."""
        # Create sentinel file
        repo.create_sentinel_file(sample_task.taskId, "done", "")
        
        # Check sentinel files
        sentinels = repo.get_sentinel_files(sample_task.taskId)
        assert sentinels["done"] is True
        assert sentinels["error"] is False
        
        # Delete sentinel file
        repo.delete_sentinel_file(sample_task.taskId, "done")
        sentinels = repo.get_sentinel_files(sample_task.taskId)
        assert sentinels["done"] is False

