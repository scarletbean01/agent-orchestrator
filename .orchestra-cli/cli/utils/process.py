"""Process management utilities for cross-platform support."""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from cli.utils.logger import logger


def get_os_name() -> str:
    """
    Returns 'windows' or 'posix'.

    This is the centralized OS detection function used throughout the codebase.
    """
    return "windows" if sys.platform == "win32" else "posix"


def is_process_alive(pid: int, pid_file: Optional[Path] = None) -> bool:
    """
    Check if a process is alive (cross-platform).

    Args:
        pid: Process ID to check
        pid_file: Optional .pid file path (for Windows tracking)

    Returns:
        True if process is running, False otherwise
    """
    try:
        if get_os_name() == "windows":
            # Windows: Use tasklist command
            # tasklist exits with 1 if pid not found
            result = subprocess.run(
                ["tasklist", "/fi", f"PID eq {pid}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False,
            )
            # Check if PID appears in output
            return str(pid) in result.stdout
        else:
            # POSIX: Send signal 0 (null signal) - doesn't kill, just checks existence
            os.kill(pid, 0)
            return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but we can't signal it (still alive)
        return True
    except FileNotFoundError:
        # tasklist not found (shouldn't happen on Windows)
        logger.warning(f"tasklist command not found (Windows check failed for PID {pid})")
        return False
    except Exception as e:
        # Defensive: log unexpected errors
        logger.warning(f"Unexpected error checking process {pid}: {e}")
        return False


def kill_process(pid: int, grace_period: int = 3) -> bool:
    """
    Kill a process gracefully, then forcefully (cross-platform).

    Args:
        pid: Process ID to kill
        grace_period: Seconds to wait before sending force kill

    Returns:
        True if process was killed or didn't exist, False on error
    """
    try:
        # Check if process exists
        if not is_process_alive(pid):
            return True  # Already dead

        if get_os_name() == "windows":
            # Windows: Use taskkill command
            try:
                # Graceful termination (sends WM_CLOSE)
                subprocess.run(
                    ["taskkill", "/pid", str(pid)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logger.debug(f"Sent graceful termination to PID {pid} (Windows)")
            except subprocess.CalledProcessError:
                # Process might have died already
                if not is_process_alive(pid):
                    return True
            except FileNotFoundError:
                logger.error(f"taskkill command not found (cannot kill PID {pid})")
                return False

            # Wait for grace period
            time.sleep(grace_period)

            # Check if still alive
            if not is_process_alive(pid):
                return True  # Gracefully terminated

            # Force kill
            try:
                subprocess.run(
                    ["taskkill", "/f", "/pid", str(pid)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logger.debug(f"Force killed PID {pid} (Windows)")
                return True
            except subprocess.CalledProcessError:
                # Process might have died during grace period
                return not is_process_alive(pid)
            except FileNotFoundError:
                logger.error(f"taskkill command not found (cannot force kill PID {pid})")
                return False

        else:
            # POSIX: Use signals (SIGTERM, then SIGKILL)
            try:
                os.kill(pid, signal.SIGTERM)
                logger.debug(f"Sent SIGTERM to PID {pid} (POSIX)")
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
                logger.debug(f"Sent SIGKILL to PID {pid} (POSIX)")
            except ProcessLookupError:
                return True  # Process died during grace period

            return True

    except ProcessLookupError:
        # Process doesn't exist
        return True
    except Exception as e:
        # Defensive: log unexpected errors
        logger.error(f"Unexpected error killing process {pid}: {e}")
        return False


def get_pid_from_file(pid_file: Path) -> Optional[int]:
    """Read PID from a .pid file."""
    try:
        return int(pid_file.read_text().strip())
    except Exception:
        return None
