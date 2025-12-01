"""Path constants for the agent orchestrator."""

from pathlib import Path


# Base paths
BASE_PATH = Path(".gemini/agents")
TASKS_DIR = BASE_PATH / "tasks"
PLANS_DIR = BASE_PATH / "plans"
LOGS_DIR = BASE_PATH / "logs"
WORKSPACE_DIR = BASE_PATH / "workspace"

# Script paths (legacy - kept for backward compatibility)
SCRIPTS_DIR = Path(".opencode/scripts")
RUN_WITH_TIMEOUT_SH = SCRIPTS_DIR / "run-with-timeout.sh"
RUN_WITH_TIMEOUT_PS1 = SCRIPTS_DIR / "run-with-timeout.ps1"

# Configuration files
AGENT_CONFIG_PATH = Path(".opencode/agent-config.json")


def ensure_directories():
    """Create all necessary directories if they don't exist."""
    for directory in [TASKS_DIR, PLANS_DIR, LOGS_DIR, WORKSPACE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
