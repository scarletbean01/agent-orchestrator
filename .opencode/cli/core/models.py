"""Data models for the agent orchestrator using Pydantic."""

from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task execution states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RetryHistoryEntry(BaseModel):
    """Record of a retry attempt."""

    attempt: int
    timestamp: datetime
    error: str
    retriedFrom: str


class Task(BaseModel):
    """Task model representing a queued agent task."""

    # Core fields
    taskId: str
    status: TaskStatus
    agent: str
    prompt: str
    planFile: str
    logFile: str
    createdAt: datetime

    # Execution fields
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    timedOutAt: Optional[datetime] = None
    retriedAt: Optional[datetime] = None
    pid: Optional[int] = None
    errorMessage: Optional[str] = None

    # Retry configuration
    retryCount: int = 0
    maxRetries: int = 3
    autoRetry: bool = False
    retryHistory: List[RetryHistoryEntry] = Field(default_factory=list)
    parentTaskId: Optional[str] = None
    retriedBy: Optional[str] = None

    # Priority and timeout
    priority: int = 5
    timeout: Optional[int] = None
    timeoutWarning: Optional[int] = None

    # Computed properties
    @property
    def is_retry(self) -> bool:
        """Check if this task is a retry attempt."""
        return self.retryCount > 0

    @property
    def elapsed_seconds(self) -> Optional[float]:
        """Calculate elapsed time in seconds for running/completed tasks."""
        if not self.startedAt:
            return None
        end = self.completedAt or self.timedOutAt or datetime.now()
        return (end - self.startedAt).total_seconds()

    @property
    def should_auto_retry(self) -> bool:
        """Check if this task should be auto-retried."""
        return (
            self.status == TaskStatus.FAILED
            and self.autoRetry
            and self.retryCount < self.maxRetries
        )

    class Config:
        """Pydantic configuration."""

        use_enum_values = False  # Keep enum types
