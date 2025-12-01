"""Task execution - launching sub-agents."""

import sys
import subprocess
from pathlib import Path
from typing import Optional

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task
from cli.core.repository import TaskRepository


class Executor:
    """Executes tasks by launching sub-agents."""

    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def launch_task(self, task: Task) -> int:
        """
        Launch a task using run-with-timeout script.

        Returns PID of launched process.
        """
        script_path = Path(".opencode/scripts/run-with-timeout.sh")

        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        # Convert timeout to string
        timeout_str = str(task.timeout) if task.timeout else "null"

        # Build command
        cmd = [str(script_path), task.taskId, timeout_str, task.agent, task.prompt]

        # Ensure log directory exists
        log_path = Path(task.logFile)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Launch in background
        log_file = open(task.logFile, "a")
        process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,  # Detach from parent
        )

        return process.pid
