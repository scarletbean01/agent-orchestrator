"""Tests for task models."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task, TaskStatus, RetryHistoryEntry


class TestTask:
    """Test cases for Task model."""

    def test_task_creation(self, sample_task):
        """Should create a task with required fields."""
        assert sample_task.taskId == "task_test_123"
        assert sample_task.status == TaskStatus.PENDING
        assert sample_task.agent == "coder"
        assert sample_task.prompt == "Test prompt"

    def test_is_retry_property(self, sample_task):
        """Should identify retry tasks."""
        assert not sample_task.is_retry
        sample_task.retryCount = 1
        assert sample_task.is_retry

    def test_is_blocked_property(self, sample_task):
        """Should identify blocked tasks."""
        assert not sample_task.is_blocked
        sample_task.blockedBy = "task_123"
        assert sample_task.is_blocked

    def test_elapsed_seconds_not_started(self, sample_task):
        """Should return None for tasks not started."""
        assert sample_task.elapsed_seconds is None

    def test_elapsed_seconds_running(self, sample_task):
        """Should calculate elapsed time for running tasks."""
        sample_task.startedAt = datetime.now() - timedelta(seconds=10)
        elapsed = sample_task.elapsed_seconds
        assert elapsed is not None
        assert 9 <= elapsed <= 11  # Allow 1 second tolerance

    def test_elapsed_seconds_completed(self, completed_task):
        """Should calculate elapsed time for completed tasks."""
        completed_task.startedAt = datetime.now() - timedelta(seconds=60)
        completed_task.completedAt = datetime.now()
        elapsed = completed_task.elapsed_seconds
        assert elapsed is not None
        assert 59 <= elapsed <= 61

    def test_should_auto_retry(self, failed_task):
        """Should identify tasks eligible for auto-retry."""
        assert not failed_task.should_auto_retry
        
        failed_task.autoRetry = True
        assert failed_task.should_auto_retry
        
        failed_task.retryCount = 3
        failed_task.maxRetries = 3
        assert not failed_task.should_auto_retry

    def test_dependencies(self, sample_task):
        """Should handle task dependencies."""
        assert len(sample_task.dependsOn) == 0
        sample_task.dependsOn = ["task_1", "task_2"]
        assert len(sample_task.dependsOn) == 2


class TestRetryHistoryEntry:
    """Test cases for RetryHistoryEntry model."""

    def test_retry_history_creation(self):
        """Should create retry history entry."""
        entry = RetryHistoryEntry(
            attempt=1,
            timestamp=datetime.now(),
            error="Test error",
            retriedFrom="task_123",
        )
        assert entry.attempt == 1
        assert entry.error == "Test error"
        assert entry.retriedFrom == "task_123"

