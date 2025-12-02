"""Tests for task scheduler."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.scheduler import Scheduler
from cli.core.models import Task, TaskStatus


class TestScheduler:
    """Test cases for Scheduler."""

    def test_get_next_pending_empty(self, repo):
        """Should return None when no pending tasks."""
        scheduler = Scheduler(repo)
        assert scheduler.get_next_pending() is None

    def test_get_next_pending_fifo(self, repo, sample_task):
        """Should return oldest pending task."""
        task1 = sample_task.model_copy()
        task1.taskId = "task_1"
        task1.createdAt = datetime.now() - timedelta(hours=2)
        
        task2 = sample_task.model_copy()
        task2.taskId = "task_2"
        task2.createdAt = datetime.now() - timedelta(hours=1)
        
        repo.save(task1)
        repo.save(task2)
        
        scheduler = Scheduler(repo)
        next_task = scheduler.get_next_pending()
        
        assert next_task.taskId == "task_1"  # Older task

    def test_priority_ordering(self, repo, sample_task):
        """Higher priority should be scheduled first."""
        task1 = sample_task.model_copy()
        task1.taskId = "task_low"
        task1.priority = 1
        task1.createdAt = datetime.now() - timedelta(hours=2)
        
        task2 = sample_task.model_copy()
        task2.taskId = "task_high"
        task2.priority = 10
        task2.createdAt = datetime.now() - timedelta(hours=1)
        
        repo.save(task1)
        repo.save(task2)
        
        scheduler = Scheduler(repo)
        next_task = scheduler.get_next_pending()
        
        assert next_task.taskId == "task_high"

    def test_get_running_count(self, repo, sample_task):
        """Should count running tasks."""
        task1 = sample_task.model_copy()
        task1.taskId = "task_1"
        task1.status = TaskStatus.RUNNING
        
        task2 = sample_task.model_copy()
        task2.taskId = "task_2"
        task2.status = TaskStatus.PENDING
        
        repo.save(task1)
        repo.save(task2)
        
        scheduler = Scheduler(repo)
        assert scheduler.get_running_count() == 1

    def test_get_pending_tasks(self, repo, sample_task):
        """Should get multiple pending tasks."""
        for i in range(5):
            task = sample_task.model_copy()
            task.taskId = f"task_{i}"
            task.createdAt = datetime.now() - timedelta(hours=i)
            repo.save(task)
        
        scheduler = Scheduler(repo)
        tasks = scheduler.get_pending_tasks(3)
        
        assert len(tasks) == 3
        # Should be oldest first
        assert tasks[0].taskId == "task_4"

    def test_skip_blocked_tasks(self, repo, sample_task):
        """Should skip blocked tasks when scheduling."""
        task1 = sample_task.model_copy()
        task1.taskId = "task_1"
        task1.blockedBy = "task_0"
        
        task2 = sample_task.model_copy()
        task2.taskId = "task_2"
        
        repo.save(task1)
        repo.save(task2)
        
        scheduler = Scheduler(repo)
        next_task = scheduler.get_next_pending()
        
        # Should skip blocked task
        assert next_task.taskId == "task_2"

