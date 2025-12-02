"""
Centralized logging utility for the agent orchestrator.

Supports:
- Environment variable control: AGENT_DEBUG=1
- Programmatic control: set_debug(True)
- Different log levels: DEBUG, INFO, WARNING, ERROR

Usage:
    from cli.utils.logger import logger
    
    logger.debug("This only shows when debug is enabled")
    logger.info("This always shows")
    logger.warning("This always shows")
    logger.error("This always shows")
    
    # Enable/disable programmatically
    logger.set_debug(True)
    logger.set_debug(False)
"""

import os
import sys


class Logger:
    """Simple logger with switchable debug output."""
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[90m",    # Gray
        "INFO": "\033[92m",     # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",    # Red
        "RESET": "\033[0m",     # Reset
    }
    
    def __init__(self):
        """Initialize logger with debug disabled by default."""
        self._debug_enabled = os.getenv("AGENT_DEBUG", "0") == "1"
        self._use_colors = self._detect_color_support()
    
    def _detect_color_support(self) -> bool:
        """Detect if terminal supports colors."""
        # Disable colors if not a TTY or on Windows without ANSI support
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
        
        # Check for NO_COLOR environment variable (standard)
        if os.getenv("NO_COLOR"):
            return False
        
        return True
    
    def set_debug(self, enabled: bool):
        """Enable or disable debug logging."""
        self._debug_enabled = enabled
    
    @property
    def debug_enabled(self) -> bool:
        """Check if debug logging is enabled."""
        return self._debug_enabled
    
    def _format_message(self, level: str, message: str) -> str:
        """Format a log message with optional colors."""
        if self._use_colors:
            color = self.COLORS.get(level, "")
            reset = self.COLORS["RESET"]
            return f"{color}{level}: {message}{reset}"
        return f"{level}: {message}"
    
    def debug(self, message: str):
        """Print debug message (only if debug is enabled)."""
        if self._debug_enabled:
            print(self._format_message("DEBUG", message))
    
    def info(self, message: str):
        """Print info message (always shown)."""
        print(self._format_message("INFO", message))
    
    def warning(self, message: str):
        """Print warning message (always shown)."""
        print(self._format_message("WARNING", message))
    
    def error(self, message: str):
        """Print error message (always shown)."""
        print(self._format_message("ERROR", message), file=sys.stderr)


# Global logger instance
logger = Logger()


# Convenience functions for direct import
def set_debug(enabled: bool):
    """Enable or disable debug logging."""
    logger.set_debug(enabled)


def debug(message: str):
    """Print debug message (only if debug is enabled)."""
    logger.debug(message)


def info(message: str):
    """Print info message (always shown)."""
    logger.info(message)


def warning(message: str):
    """Print warning message (always shown)."""
    logger.warning(message)


def error(message: str):
    """Print error message (always shown)."""
    logger.error(message)


def is_debug_enabled() -> bool:
    """Check if debug logging is enabled."""
    return logger.debug_enabled

