"""Run command implementation - executes pending tasks."""

import sys
from pathlib import Path
from datetime import datetime

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.repository import TaskRepository
from cli.core.scheduler import Scheduler
from cli.core.executor import Executor
from cli.core.models import TaskStatus


def run_command(parallel: int = None):
    """
    Execute pending task(s).

    Args:
        parallel: If specified, run up to N tasks in parallel
    """
    repo = TaskRepository()
    scheduler = Scheduler(repo)
    executor = Executor(repo)

    if parallel:
        # Parallel execution
        running_count = scheduler.get_running_count()
        available = parallel - running_count

        if available <= 0:
            print(
                f"\033[93mAlready running {running_count} tasks (max: {parallel})\033[0m"
            )  # Yellow
            return

        tasks = scheduler.get_pending_tasks(available)
        if not tasks:
            print("\033[93mNo pending tasks\033[0m")  # Yellow
            return

        started = []
        for task in tasks:
            try:
                task.status = TaskStatus.RUNNING
                task.startedAt = datetime.now()
                task.pid = executor.launch_task(task)
                repo.save(task)
                started.append((task.taskId, task.pid))
            except Exception as e:
                print(f"\033[91mError starting {task.taskId}: {e}\033[0m")  # Red
                task.status = TaskStatus.FAILED
                task.errorMessage = str(e)
                repo.save(task)

        if started:
            print(f"\033[92mStarted {len(started)} task(s):\033[0m")  # Green
            for task_id, pid in started:
                print(f"  {task_id} (PID: {pid})")
    else:
        # Single task execution
        task = scheduler.get_next_pending()
        if not task:
            print("\033[93mNo pending tasks\033[0m")  # Yellow
            return

        try:
            task.status = TaskStatus.RUNNING
            task.startedAt = datetime.now()
            task.pid = executor.launch_task(task)
            repo.save(task)

            print(
                f"\033[92mStarted task {task.taskId} (PID: {task.pid})\033[0m"
            )  # Green
            if task.timeout:
                print(f"  Timeout: {task.timeout}s")
        except Exception as e:
            print(f"\033[91mError starting task: {e}\033[0m")  # Red
            task.status = TaskStatus.FAILED
            task.errorMessage = str(e)
            repo.save(task)
