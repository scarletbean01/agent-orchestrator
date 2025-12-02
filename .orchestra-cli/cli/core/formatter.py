"""Formatting utilities for displaying task information."""

import sys
from typing import List, Dict

from .models import Task, TaskStatus
from ..utils.time_utils import format_elapsed


class Formatter:
    """Formats task information for console output."""

    # Status icons (with ASCII fallback for Windows)
    STATUS_ICONS = {
        TaskStatus.PENDING: "⏸",
        TaskStatus.RUNNING: "⏱",
        TaskStatus.COMPLETE: "✓",
        TaskStatus.FAILED: "✗",
        TaskStatus.CANCELLED: "⊗",
    }

    # ASCII fallback icons for Windows console
    STATUS_ICONS_ASCII = {
        TaskStatus.PENDING: "[ ]",
        TaskStatus.RUNNING: "[>]",
        TaskStatus.COMPLETE: "[+]",
        TaskStatus.FAILED: "[X]",
        TaskStatus.CANCELLED: "[-]",
    }

    @staticmethod
    def _supports_unicode():
        """Check if console supports Unicode."""
        return sys.stdout.encoding.lower() not in ("cp1252", "ascii", "cp437")

    def print_task_table(self, tasks: List[Task]):
        """Print a formatted table of tasks."""
        if not tasks:
            print("\033[93mNo tasks found\033[0m")  # Yellow
            return

        # Table header
        print("\n" + "=" * 120)
        print(
            f"{'ID':<22} {'Agent':<8} {'Status':<10} {'Prompt':<40} {'Time':<15} {'Retry':<8} {'Error/Info':<30}"
        )
        print("=" * 120)

        # Table rows
        for task in tasks:
            # Format ID (use ASCII arrow for Windows)
            retry_prefix = ">" if not self._supports_unicode() else "↻"
            task_id = f"{retry_prefix} {task.taskId}" if task.is_retry else task.taskId

            # Format status (use appropriate icon set)
            icons = (
                self.STATUS_ICONS
                if self._supports_unicode()
                else self.STATUS_ICONS_ASCII
            )

            # Check if blocked
            if task.is_blocked:
                icon = "🚫" if self._supports_unicode() else "[B]"
                status_str = f"{icon} blocked"
            else:
                icon = icons.get(task.status, "?")
                status_str = f"{icon} {task.status.value}"

            # Format time
            time_str = (
                format_elapsed(task) if task.status == TaskStatus.RUNNING else "-"
            )

            # Format retry
            retry_str = (
                f"{task.retryCount}/{task.maxRetries}" if task.retryCount > 0 else "-"
            )

            # Format error/info
            info_str = ""
            if task.is_blocked:
                info_str = task.blockedReason[:30] if task.blockedReason else "blocked"
            elif task.status == TaskStatus.FAILED and task.errorMessage:
                info_str = task.errorMessage[:30]
            elif task.autoRetry and task.status == TaskStatus.FAILED:
                info_str = "auto-retry pending"
            elif task.dependsOn:
                info_str = f"deps: {len(task.dependsOn)}"

            # Truncate long strings
            prompt_str = (
                task.prompt[:40] + "..." if len(task.prompt) > 40 else task.prompt
            )

            # Print row
            print(
                f"{task_id:<22} {task.agent:<8} {status_str:<10} {prompt_str:<40} {time_str:<15} {retry_str:<8} {info_str:<30}"
            )

        print("=" * 120 + "\n")

    def print_summary(self, tasks: List[Task]):
        """Print summary statistics."""
        stats = self._calculate_stats(tasks)

        print("\033[1mSummary:\033[0m")  # Bold
        print(f"  Total: {stats['total']}")
        print(f"  Running: {stats['running']}")
        print(f"  Pending: {stats['pending']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Cancelled: {stats['cancelled']}")
        print()

    def _calculate_stats(self, tasks: List[Task]) -> Dict[str, int]:
        """Calculate task statistics."""
        stats = {
            "total": len(tasks),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }

        for task in tasks:
            if task.status == TaskStatus.PENDING:
                stats["pending"] += 1
            elif task.status == TaskStatus.RUNNING:
                stats["running"] += 1
            elif task.status == TaskStatus.COMPLETE:
                stats["completed"] += 1
            elif task.status == TaskStatus.FAILED:
                stats["failed"] += 1
            elif task.status == TaskStatus.CANCELLED:
                stats["cancelled"] += 1

        return stats
