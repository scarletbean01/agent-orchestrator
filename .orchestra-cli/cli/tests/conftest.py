"""Pytest fixtures for orchestrator tests."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.repository import TaskRepository
from cli.core.models import Task, TaskStatus


@pytest.fixture
def temp_orchestra_dir(tmp_path, monkeypatch):
    """Create a temporary .orchestra directory."""
    orchestra_dir = tmp_path / ".orchestra"
    orchestra_dir.mkdir()
    (orchestra_dir / "tasks").mkdir()
    (orchestra_dir / "plans").mkdir()
    (orchestra_dir / "logs").mkdir()
    (orchestra_dir / "archive").mkdir()
    
    # Monkeypatch the paths module to use temp directory
    monkeypatch.setattr("cli.utils.paths.ORCHESTRA_DIR", str(orchestra_dir))
    monkeypatch.setattr("cli.utils.paths.TASKS_DIR", str(orchestra_dir / "tasks"))
    monkeypatch.setattr("cli.utils.paths.PLANS_DIR", str(orchestra_dir / "plans"))
    monkeypatch.setattr("cli.utils.paths.LOGS_DIR", str(orchestra_dir / "logs"))
    
    return orchestra_dir


@pytest.fixture
def repo(temp_orchestra_dir):
    """Create a TaskRepository with temp directory."""
    return TaskRepository()


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return Task(
        taskId="task_test_123",
        status=TaskStatus.PENDING,
        agent="coder",
        prompt="Test prompt",
        planFile=".orchestra/plans/task_test_123_plan.md",
        logFile=".orchestra/logs/task_test_123.log",
        createdAt=datetime.now(),
    )


@pytest.fixture
def completed_task():
    """Create a completed task for testing."""
    return Task(
        taskId="task_completed_456",
        status=TaskStatus.COMPLETE,
        agent="coder",
        prompt="Completed task",
        planFile=".orchestra/plans/task_completed_456_plan.md",
        logFile=".orchestra/logs/task_completed_456.log",
        createdAt=datetime.now(),
        completedAt=datetime.now(),
    )


@pytest.fixture
def failed_task():
    """Create a failed task for testing."""
    return Task(
        taskId="task_failed_789",
        status=TaskStatus.FAILED,
        agent="coder",
        prompt="Failed task",
        planFile=".orchestra/plans/task_failed_789_plan.md",
        logFile=".orchestra/logs/task_failed_789.log",
        createdAt=datetime.now(),
        completedAt=datetime.now(),
        errorMessage="Test error",
    )

