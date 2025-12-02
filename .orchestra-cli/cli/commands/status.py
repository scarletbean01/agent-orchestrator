"""Status command implementation."""

import sys
import time
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.repository import TaskRepository
from cli.core.reconciler import Reconciler
from cli.core.formatter import Formatter
from cli.core.retry_manager import RetryManager
from cli.core.models import TaskStatus


def status_command(watch: bool = False, interval: int = 5, auto_retry: bool = True):
    """
    Show task queue status and reconcile completed tasks.

    Args:
        watch: If True, continuously refresh the display
        interval: Seconds between refreshes in watch mode
        auto_retry: If True, trigger auto-retry for eligible tasks
    """

    def _display_status():
        """Display status once."""
        repo = TaskRepository()
        reconciler = Reconciler(repo)
        formatter = Formatter()

        # Reconcile running tasks
        changed = reconciler.reconcile_all()
        if changed:
            print(f"\033[93mReconciled {changed} task(s)\033[0m\n")  # Yellow

        # Auto-retry logic
        if auto_retry:
            retry_manager = RetryManager(repo)
            tasks = repo.load_all()  # Reload in case reconciliation changed things
            for task in tasks:
                if task.status == TaskStatus.FAILED and task.autoRetry:
                    if retry_manager.is_retry_due(task):
                        new_task = retry_manager.create_retry_task(
                            task, auto_retry=True
                        )
                        if new_task:
                            print(
                                f"\033[96mAuto-retrying {task.taskId} (attempt {new_task.retryCount}/{new_task.maxRetries})\033[0m"
                            )

        # Load and display tasks
        tasks = repo.load_all()

        print("\033[1m\033[96mTask Queue Status\033[0m")  # Bold Cyan
        formatter.print_task_table(tasks)
        formatter.print_summary(tasks)

    if watch:
        # Watch mode: clear screen and refresh
        try:
            while True:
                # Clear screen (ANSI escape code)
                print("\033[2J\033[H", end="")
                _display_status()
                print(
                    f"\n\033[90mRefreshing every {interval}s (Ctrl+C to exit)...\033[0m"
                )
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\033[92mWatch mode stopped\033[0m")  # Green
    else:
        _display_status()
