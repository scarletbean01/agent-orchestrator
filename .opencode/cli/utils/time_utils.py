"""Time formatting utilities."""

from datetime import datetime, timedelta
from typing import Optional
from ..core.models import Task, TaskStatus


def format_duration(seconds: int) -> str:
    """
    Format seconds into human-readable duration.

    Examples:
        30 -> "30s"
        90 -> "1m 30s"
        3661 -> "1h 1m"
        86400 -> "1d"
    """
    if seconds < 60:
        return f"{seconds}s"

    minutes = seconds // 60
    seconds = seconds % 60

    if minutes < 60:
        if seconds > 0:
            return f"{minutes}m {seconds}s"
        return f"{minutes}m"

    hours = minutes // 60
    minutes = minutes % 60

    if hours < 24:
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"

    days = hours // 24
    hours = hours % 24

    if hours > 0:
        return f"{days}d {hours}h"
    return f"{days}d"


def format_elapsed(task: Task) -> str:
    """
    Format elapsed time for a task with optional timeout display.

    Examples:
        "5m 30s" (running without timeout)
        "5m 30s / 1h" (running with timeout)
        "⚠ 58m / 1h" (near timeout warning)
        "-" (not started)
    """
    if not task.startedAt or task.status != TaskStatus.RUNNING:
        return "-"

    elapsed = task.elapsed_seconds
    if not elapsed:
        return "-"

    elapsed_str = format_duration(int(elapsed))

    if task.timeout:
        timeout_str = format_duration(task.timeout)
        remaining = task.timeout - elapsed

        # Warning if near timeout
        if task.timeoutWarning and remaining <= task.timeoutWarning:
            return f"⚠ {elapsed_str} / {timeout_str}"

        return f"{elapsed_str} / {timeout_str}"

    return elapsed_str


def format_timestamp(dt: Optional[datetime]) -> str:
    """Format a datetime as ISO timestamp or '-' if None."""
    if not dt:
        return "-"
    return dt.isoformat()
