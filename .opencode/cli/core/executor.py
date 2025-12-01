"""Task execution - launching sub-agents."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task
from cli.core.repository import TaskRepository
from cli.utils.process import get_os_name
from cli.utils.paths import AGENT_CONFIG_PATH


class Executor:
    """Executes tasks by launching sub-agents."""

    def __init__(self, repo: TaskRepository):
        self.repo = repo
        self.agent_configs = self._load_agent_configs()

    def _load_agent_configs(self) -> Dict[str, Any]:
        """Load agent configurations from JSON file."""
        if not AGENT_CONFIG_PATH.exists():
            print(
                f"INFO: Agent config not found at {AGENT_CONFIG_PATH}, using defaults"
            )
            return {}

        try:
            with open(AGENT_CONFIG_PATH) as f:
                config = json.load(f)
                agents = config.get("agents", {})
                print(
                    f"INFO: Loaded {len(agents)} agent configurations from {AGENT_CONFIG_PATH}"
                )
                return agents
        except Exception as e:
            print(f"WARNING: Failed to load agent config: {e}")
            return {}

    def _build_command(self, task: Task) -> List[str]:
        """
        Build the command to execute based on agent configuration.

        Uses agent-config.json if available, otherwise falls back to default 'opencode run'.
        This maintains backward compatibility while enabling agent decoupling.
        """
        agent_config = self.agent_configs.get(task.agent)

        if agent_config:
            # Dynamic command construction from agent-config.json
            print(f"DEBUG: Building command for agent '{task.agent}' using config")
            base_cmd = [agent_config["command"]]
            args = agent_config["args"]

            # Variable substitution
            prompt = f"Your Task ID is {task.taskId}. Task: {task.prompt}. Signal completion by creating .gemini/agents/tasks/{task.taskId}.done"

            processed_args = []
            for arg in args:
                arg = arg.replace("{prompt}", prompt)
                arg = arg.replace("{taskId}", task.taskId)
                arg = arg.replace("{agent}", task.agent)
                processed_args.append(arg)

            return base_cmd + processed_args
        else:
            # Default legacy behavior (backward compatibility)
            print(
                f"DEBUG: Agent '{task.agent}' not in config, using default 'opencode run'"
            )
            prompt = f"Your Task ID is {task.taskId}. Task: {task.prompt}. Signal completion by creating .gemini/agents/tasks/{task.taskId}.done"
            return ["opencode", "run", prompt, "--agent", task.agent]

    def launch_task(self, task: Task) -> int:
        """
        Launch a task in a detached process and handle timeout.

        Pure Python implementation - no shell scripts required.
        Cross-platform (Windows/macOS/Linux).
        """
        cmd = self._build_command(task)

        print(
            f"DEBUG: Launching task {task.taskId} with command: {' '.join(cmd[:2])}..."
        )

        # Ensure log directory exists
        log_path = Path(task.logFile)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Platform-specific process creation
        creation_flags = 0
        if get_os_name() == "windows":
            # CREATE_NEW_PROCESS_GROUP allows Ctrl+C isolation on Windows
            creation_flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            print(
                f"DEBUG: Using Windows process creation (creationflags={creation_flags})"
            )
        else:
            print(f"DEBUG: Using POSIX process creation (start_new_session=True)")

        log_file = open(task.logFile, "a")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=creation_flags,  # Windows
                start_new_session=True,  # POSIX
            )

            print(
                f"INFO: Task {task.taskId} launched successfully (PID: {process.pid})"
            )
        except Exception as e:
            print(f"ERROR: Failed to launch task {task.taskId}: {e}")
            log_file.close()
            raise

        # Start a thread to monitor the process and handle timeout
        import threading

        monitor_thread = threading.Thread(
            target=self._monitor_process, args=(process, task, log_file)
        )
        monitor_thread.daemon = True
        monitor_thread.start()

        return process.pid

    def _monitor_process(self, process: subprocess.Popen, task: Task, log_file):
        """
        Monitor the subprocess for completion or timeout.

        This runs in a separate thread and handles:
        - Normal completion (exit code capture)
        - Timeout (force kill + sentinel file)
        - Exit code recording
        """
        exit_code = -1  # Default exit code
        try:
            if task.timeout:
                # Wait with timeout
                print(
                    f"DEBUG: Waiting for task {task.taskId} (timeout: {task.timeout}s)"
                )
                process.wait(timeout=task.timeout)
                exit_code = process.returncode
                print(f"DEBUG: Task {task.taskId} completed with exit code {exit_code}")
            else:
                # Wait indefinitely
                print(f"DEBUG: Waiting for task {task.taskId} (no timeout)")
                process.wait()
                exit_code = process.returncode
                print(f"DEBUG: Task {task.taskId} completed with exit code {exit_code}")

        except subprocess.TimeoutExpired:
            # Timeout occurred - kill the process
            exit_code = 124  # GNU timeout exit code for timeout
            print(
                f"WARNING: Task {task.taskId} timed out after {task.timeout}s, killing process..."
            )

            from cli.utils.process import kill_process

            kill_process(process.pid)

            # Log timeout
            timestamp = datetime.now().isoformat()
            timeout_info = f'{{"timeout": {task.timeout}, "timestamp": "{timestamp}"}}'
            self.repo.write_sentinel_file(task.taskId, "timeout", timeout_info)
            print(f"Task {task.taskId} timed out after {task.timeout}s", file=log_file)

        except Exception as e:
            # Unexpected error during monitoring
            print(f"ERROR: Unexpected error monitoring task {task.taskId}: {e}")
            exit_code = -2

        finally:
            # Record exit code
            self.repo.write_sentinel_file(task.taskId, "exitcode", str(exit_code))
            log_file.close()
            print(
                f"DEBUG: Task {task.taskId} monitoring thread exiting (exit code: {exit_code})"
            )
