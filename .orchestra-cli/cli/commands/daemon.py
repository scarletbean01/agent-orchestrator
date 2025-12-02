"""Daemon command implementation - continuous task execution."""

import signal
import sys
import time
from datetime import datetime
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.repository import TaskRepository
from cli.core.reconciler import Reconciler
from cli.core.scheduler import Scheduler
from cli.core.executor import Executor
from cli.core.retry_manager import RetryManager
from cli.core.archive_manager import ArchiveManager
from cli.core.models import TaskStatus
from cli.utils.logger import logger


class DaemonRunner:
    """Daemon for continuous task execution and monitoring."""

    def __init__(self, max_concurrent: int = 3, interval: int = 5):
        self.max_concurrent = max_concurrent
        self.interval = interval
        self.running = True
        self.repo = TaskRepository()
        self.reconciler = Reconciler(self.repo)
        self.scheduler = Scheduler(self.repo)
        self.executor = Executor(self.repo)
        self.retry_manager = RetryManager(self.repo)
        self.archive_manager = ArchiveManager(self.repo)

        # Archive check interval (1 hour)
        self.archive_interval = 3600
        self.last_archive_check = 0

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"\nReceived signal {signum}, shutting down gracefully...")
        self.running = False

    def _reconcile(self):
        """Reconcile task states."""
        try:
            changed = self.reconciler.reconcile_all()
            if changed:
                logger.info(f"Reconciled {changed} task(s)")
            return changed
        except Exception as e:
            logger.error(f"Reconciliation error: {e}")
            return 0

    def _auto_retry(self):
        """Check for tasks that need automatic retry."""
        try:
            tasks = self.repo.load_all()
            retry_count = 0
            for task in tasks:
                if task.status == TaskStatus.FAILED and task.autoRetry:
                    if self.retry_manager.is_retry_due(task):
                        new_task = self.retry_manager.create_retry_task(
                            task, auto_retry=True
                        )
                        if new_task:
                            logger.info(
                                f"Auto-retrying {task.taskId} (attempt {new_task.retryCount}/{new_task.maxRetries})"
                            )
                            retry_count += 1
            return retry_count
        except Exception as e:
            logger.error(f"Auto-retry error: {e}")
            return 0

    def _launch_tasks(self):
        """Launch pending tasks up to the concurrency limit."""
        try:
            running_count = self.scheduler.get_running_count()
            available = self.max_concurrent - running_count

            if available <= 0:
                return 0

            pending_tasks = self.scheduler.get_pending_tasks(available)
            if not pending_tasks:
                return 0

            launched = 0
            for task in pending_tasks:
                try:
                    task.status = TaskStatus.RUNNING
                    task.startedAt = datetime.now()
                    task.pid = self.executor.launch_task(task)
                    self.repo.save(task)
                    logger.info(
                        f"Launched task {task.taskId} (PID: {task.pid}, agent: {task.agent})"
                    )
                    launched += 1
                except Exception as e:
                    logger.error(f"Failed to launch {task.taskId}: {e}")
                    task.status = TaskStatus.FAILED
                    task.errorMessage = str(e)
                    self.repo.save(task)

            return launched
        except Exception as e:
            logger.error(f"Task launch error: {e}")
            return 0

    def _get_status_summary(self):
        """Get a summary of current task states."""
        tasks = self.repo.load_all()
        counts = {
            "total": len(tasks),
            "running": sum(1 for t in tasks if t.status == TaskStatus.RUNNING),
            "pending": sum(1 for t in tasks if t.status == TaskStatus.PENDING),
            "completed": sum(1 for t in tasks if t.status == TaskStatus.COMPLETE),
            "failed": sum(1 for t in tasks if t.status == TaskStatus.FAILED),
            "cancelled": sum(1 for t in tasks if t.status == TaskStatus.CANCELLED),
        }
        return counts

    def run(self):
        """Main daemon loop."""
        logger.info("=" * 60)
        logger.info("Agent Orchestrator Daemon Started")
        logger.info(f"Max concurrent tasks: {self.max_concurrent}")
        logger.info(f"Check interval: {self.interval}s")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)

        cycle = 0
        while self.running:
            try:
                cycle += 1
                logger.debug(f"\n--- Cycle {cycle} ---")

                # 1. Reconcile task states
                reconciled = self._reconcile()

                # 2. Auto-retry failed tasks
                retried = self._auto_retry()

                # 3. Launch pending tasks
                launched = self._launch_tasks()

                # 4. Show status summary
                status = self._get_status_summary()
                logger.info(
                    f"Status: {status['running']} running, "
                    f"{status['pending']} pending, "
                    f"{status['completed']} completed, "
                    f"{status['failed']} failed"
                )

                if reconciled or retried or launched:
                    logger.debug(
                        f"Actions: reconciled={reconciled}, retried={retried}, launched={launched}"
                    )

                # 5. Periodic archival check (every hour)
                current_time = time.time()
                if current_time - self.last_archive_check > self.archive_interval:
                    archived, _ = self.archive_manager.run_archival()
                    if archived:
                        logger.info(f"Archived {archived} old task(s)")
                    self.archive_manager.check_queue_size()
                    self.last_archive_check = current_time

                # 6. Sleep until next cycle
                time.sleep(self.interval)

            except KeyboardInterrupt:
                logger.info("\nKeyboardInterrupt received, stopping...")
                self.running = False
            except Exception as e:
                logger.error(f"Daemon error: {e}")
                time.sleep(self.interval)

        logger.info("\nDaemon stopped")


def daemon_command(max_concurrent: int = 3, interval: int = 5):
    """
    Run the orchestrator in daemon mode.

    Args:
        max_concurrent: Maximum number of concurrent tasks (default: 3)
        interval: Check interval in seconds (default: 5)
    """
    # Validate arguments
    if max_concurrent < 1:
        print("Error: max_concurrent must be >= 1")
        sys.exit(1)

    if interval < 1:
        print("Error: interval must be >= 1 second")
        sys.exit(1)

    # Create and run daemon
    daemon = DaemonRunner(max_concurrent, interval)
    try:
        daemon.run()
    except KeyboardInterrupt:
        print("\nDaemon stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
