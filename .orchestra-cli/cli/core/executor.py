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
from cli.utils.logger import logger


class Executor:
    """Executes tasks by launching sub-agents."""

    def __init__(self, repo: TaskRepository):
        self.repo = repo
        self.agent_configs = self._load_agent_configs()

    def _load_agent_configs(self) -> Dict[str, Any]:
        """Load agent configurations from JSON file."""
        if not AGENT_CONFIG_PATH.exists():
            logger.info(
                f"Agent config not found at {AGENT_CONFIG_PATH}, using defaults"
            )
            return {}

        try:
            with open(AGENT_CONFIG_PATH) as f:
                config = json.load(f)
                agents = config.get("agents", {})
                logger.info(
                    f"Loaded {len(agents)} agent configurations from {AGENT_CONFIG_PATH}"
                )
                return agents
        except Exception as e:
            logger.warning(f"Failed to load agent config: {e}")
            return {}

    def _build_command(self, task: Task) -> List[str]:
        """
        Build the command to execute based on agent configuration.

        Uses agent-config.json if available, otherwise falls back to default 'opencode run'.
        This maintains backward compatibility while enabling agent decoupling.

        Supports prompt templates via:
        - promptTemplateFile: Path to a template file
        - promptTemplate: Inline template string
        """
        agent_config = self.agent_configs.get(task.agent)

        if agent_config:
            # Dynamic command construction from agent-config.json
            logger.debug(f"Building command for agent '{task.agent}' using config")
            base_cmd = [agent_config["command"]]
            args = agent_config["args"]

            # Build the prompt - check for template
            if "promptTemplateFile" in agent_config:
                prompt = self._load_prompt_template(
                    agent_config["promptTemplateFile"], task
                )
            elif "promptTemplate" in agent_config:
                prompt = self._format_prompt_template(
                    agent_config["promptTemplate"], task
                )
            else:
                # Fallback to basic prompt
                prompt = self._build_basic_prompt(task)

            # Platform-specific escaping for Windows shell compatibility
            if get_os_name() == "windows":
                # On Windows with shell=True, newlines break argument parsing
                # Replace actual newlines with escaped newlines
                prompt = prompt.replace("\n", "\\n")
                logger.debug(
                    f"Escaped newlines for Windows shell (prompt length: {len(prompt)} chars)"
                )

            # Variable substitution in args
            processed_args = []
            for arg in args:
                arg = arg.replace("{prompt}", prompt)
                arg = arg.replace("{taskId}", task.taskId)
                arg = arg.replace("{agent}", task.agent)
                processed_args.append(arg)

            return base_cmd + processed_args
        else:
            # Default legacy behavior (backward compatibility)
            logger.debug(
                f"Agent '{task.agent}' not in config, using default 'opencode run'"
            )
            prompt = self._build_basic_prompt(task)

            # Platform-specific escaping for Windows shell compatibility
            if get_os_name() == "windows":
                prompt = prompt.replace("\n", "\\n")
                logger.debug(
                    f"Escaped newlines for Windows shell (prompt length: {len(prompt)} chars)"
                )

            return ["opencode", "run", prompt, "--agent", task.agent]

    def _build_basic_prompt(self, task: Task) -> str:
        """Build basic prompt (current behavior)."""
        return f"Your Task ID is {task.taskId}. Task: {task.prompt}. Signal completion by creating .orchestra/tasks/{task.taskId}.done"

    def _load_prompt_template(self, template_file: str, task: Task) -> str:
        """
        Load and format prompt from template file.

        Args:
            template_file: Path to template file (relative to project root)
            task: Task object with variables for substitution

        Returns:
            Formatted prompt string
        """
        template_path = Path(template_file)
        if not template_path.exists():
            logger.warning(
                f"Template file {template_file} not found, using basic prompt"
            )
            return self._build_basic_prompt(task)

        try:
            template = template_path.read_text(encoding="utf-8")
            logger.debug(f"Loaded prompt template from {template_file}")
            return self._format_prompt_template(template, task)
        except Exception as e:
            logger.warning(f"Failed to load template {template_file}: {e}")
            return self._build_basic_prompt(task)

    def _format_prompt_template(self, template: str, task: Task) -> str:
        """
        Format template with task variables.

        Available variables:
        - {taskId}: Task ID
        - {userPrompt}: User's original task prompt
        - {planFile}: Path to plan file
        - {logFile}: Path to log file
        - {agent}: Agent name

        Args:
            template: Template string with {variable} placeholders
            task: Task object with values for substitution

        Returns:
            Formatted prompt string
        """
        try:
            return template.format(
                taskId=task.taskId,
                userPrompt=task.prompt,
                planFile=task.planFile,
                logFile=task.logFile,
                agent=task.agent,
            )
        except KeyError as e:
            logger.warning(f"Template variable {e} not found, using basic prompt")
            return self._build_basic_prompt(task)

    def launch_task(self, task: Task) -> int:
        """
        Launch a task in a detached process and handle timeout.

        Pure Python implementation - no shell scripts required.
        Cross-platform (Windows/macOS/Linux).
        """
        cmd = self._build_command(task)

        # Debug logging: Show full command
        logger.debug(f"Launching task {task.taskId}")
        logger.debug(f"Agent: {task.agent}")
        logger.debug(f"Command array length: {len(cmd)} elements")
        logger.debug(f"Full command: {cmd}")

        # Show command in a more readable format
        if len(cmd) > 0:
            logger.debug(f"Executable: {cmd[0]}")
            if len(cmd) > 1:
                logger.debug(f"Arguments ({len(cmd) - 1}):")
                for i, arg in enumerate(cmd[1:], 1):
                    # Truncate long arguments (like prompts) for readability
                    if len(arg) > 100:
                        logger.debug(f"  [{i}] {arg[:100]}... ({len(arg)} chars)")
                    else:
                        logger.debug(f"  [{i}] {arg}")

        # Ensure log directory exists
        log_path = Path(task.logFile)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Platform-specific process creation
        creation_flags = 0
        use_shell = False
        if get_os_name() == "windows":
            # CREATE_NEW_PROCESS_GROUP allows Ctrl+C isolation on Windows
            creation_flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            # On Windows, shell=True is needed to run .cmd/.ps1 scripts (like npx, opencode)
            use_shell = True
            logger.debug(
                f"Using Windows process creation (creationflags={creation_flags}, shell=True)"
            )
        else:
            logger.debug("Using POSIX process creation (start_new_session=True)")

        log_file = open(task.logFile, "a")

        # Convert command list to string for shell mode on Windows
        if use_shell:
            cmd_for_popen = subprocess.list2cmdline(cmd)
            logger.debug(f"Shell command string: {cmd_for_popen[:200]}...")
        else:
            cmd_for_popen = cmd
            logger.debug("Direct command execution (no shell)")

        try:
            process = subprocess.Popen(
                cmd_for_popen,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=creation_flags,  # Windows
                start_new_session=True,  # POSIX
                shell=use_shell,
            )
            logger.info(
                f"Task {task.taskId} launched successfully (PID: {process.pid})"
            )
        except Exception as e:
            logger.error(f"Failed to launch task {task.taskId}: {e}")
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
                logger.debug(
                    f"Waiting for task {task.taskId} (timeout: {task.timeout}s)"
                )
                process.wait(timeout=task.timeout)
                exit_code = process.returncode
                logger.debug(f"Task {task.taskId} completed with exit code {exit_code}")
            else:
                # Wait indefinitely
                logger.debug(f"Waiting for task {task.taskId} (no timeout)")
                process.wait()
                exit_code = process.returncode
                logger.debug(f"Task {task.taskId} completed with exit code {exit_code}")

        except subprocess.TimeoutExpired:
            # Timeout occurred - kill the process
            exit_code = 124  # GNU timeout exit code for timeout
            logger.warning(
                f"Task {task.taskId} timed out after {task.timeout}s, killing process..."
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
            logger.error(f"Unexpected error monitoring task {task.taskId}: {e}")
            exit_code = -2

        finally:
            # Record exit code
            self.repo.write_sentinel_file(task.taskId, "exitcode", str(exit_code))
            log_file.close()
            logger.debug(
                f"Task {task.taskId} monitoring thread exiting (exit code: {exit_code})"
            )
