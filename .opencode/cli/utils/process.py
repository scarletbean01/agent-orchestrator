"""Process management utilities for cross-platform support."""

import os
import signal
import time
from pathlib import Path
from typing import Optional


def is_process_alive(pid: int, pid_file: Optional[Path] = None) -> bool:
    """
    Check if a process is alive.

    Args:
        pid: Process ID to check
        pid_file: Optional .pid file path (for Windows tracking)

    Returns:
        True if process is running, False otherwise
    """
    try:
        # Send signal 0 (null signal) - doesn't kill, just checks existence
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but we can't signal it (still alive)
        return True
    except Exception:
        return False


def kill_process(pid: int, grace_period: int = 3) -> bool:
    """
    Kill a process gracefully (SIGTERM), then forcefully (SIGKILL).

    Args:
        pid: Process ID to kill
        grace_period: Seconds to wait before sending SIGKILL

    Returns:
        True if process was killed or didn't exist, False on error
    """
    try:
        # Check if process exists
        if not is_process_alive(pid):
            return True  # Already dead

        # Try graceful termination (SIGTERM)
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            return True  # Process died before we could send signal

        # Wait for grace period
        time.sleep(grace_period)

        # Check if still alive
        if not is_process_alive(pid):
            return True  # Gracefully terminated

        # Force kill (SIGKILL)
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            return True  # Process died during grace period

        return True

    except ProcessLookupError:
        # Process doesn't exist
        return True
    except Exception:
        # Other error occurred
        return False


def get_pid_from_file(pid_file: Path) -> Optional[int]:
    """Read PID from a .pid file."""
    try:
        return int(pid_file.read_text().strip())
    except Exception:
        return None
