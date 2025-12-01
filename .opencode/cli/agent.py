"""Minimal CLI implementation using only Python stdlib.

This is a simplified version that doesn't require Click or Rich.
It provides the same functionality with basic formatting.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class Console:
    """Simple console wrapper for colored output."""

    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }

    def print(self, text: str, style: str = ""):
        """Print with optional styling."""
        if style in self.COLORS:
            print(f"{self.COLORS[style]}{text}{self.COLORS['reset']}")
        else:
            # Handle [color] tags
            for color, code in self.COLORS.items():
                text = text.replace(f"[{color}]", code)
                text = text.replace(f"[/{color}]", self.COLORS["reset"])
            print(text)


console = Console()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="agent-orchestrator",
        description="OpenCode Agent Orchestrator v2.0 - Task queue management for AI agents",
    )
    parser.add_argument(
        "--version", action="store_true", help="Show version information"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show task queue status")
    status_parser.add_argument(
        "--watch", "-w", action="store_true", help="Auto-refresh every N seconds"
    )
    status_parser.add_argument(
        "--interval", "-i", type=int, default=5, help="Watch interval in seconds"
    )
    status_parser.add_argument(
        "--no-auto-retry", action="store_true", help="Skip auto-retry logic"
    )

    # Start command
    start_parser = subparsers.add_parser("start", help="Queue a new agent task")
    start_parser.add_argument("agent", help="Agent name (e.g., coder)")
    start_parser.add_argument("prompt", help="Task prompt/description")
    start_parser.add_argument(
        "--max-retries", type=int, default=3, help="Maximum retry attempts"
    )
    start_parser.add_argument(
        "--auto-retry", action="store_true", help="Enable automatic retries"
    )
    start_parser.add_argument(
        "--priority", type=int, default=5, help="Task priority (1-10)"
    )
    start_parser.add_argument("--timeout", type=int, help="Timeout in seconds")

    # Run command
    run_parser = subparsers.add_parser("run", help="Execute pending task(s)")
    run_parser.add_argument(
        "--parallel", "-p", type=int, help="Run N tasks in parallel"
    )

    # Cancel command
    cancel_parser = subparsers.add_parser(
        "cancel", help="Cancel a running or pending task"
    )
    cancel_parser.add_argument("task_id", help="Task ID to cancel")

    # Retry command
    retry_parser = subparsers.add_parser("retry", help="Retry a failed task")
    retry_parser.add_argument("task_id", help="Task ID to retry")
    retry_parser.add_argument("--max-retries", type=int, help="Override max retries")
    retry_parser.add_argument(
        "--auto", action="store_true", help="Enable auto-retry for this retry"
    )

    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Remove old task files")
    clean_parser.add_argument(
        "filter",
        nargs="?",
        default="completed",
        help="Filter: completed, failed, cancelled, all, or task_id",
    )
    clean_parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation"
    )

    # Timeout command
    timeout_parser = subparsers.add_parser("timeout", help="Manage task timeouts")
    timeout_parser.add_argument(
        "subcommand", help="list, extend, or task_id to timeout"
    )
    timeout_parser.add_argument("args", nargs="*", help="Additional arguments")

    args = parser.parse_args()

    if args.version:
        console.print("[bold]OpenCode Agent Orchestrator[/bold] v2.0.0", "bold")
        console.print("Python-based task queue management system")
        return

    if not args.command:
        parser.print_help()
        return

    # Import commands here to avoid import errors if dependencies missing
    try:
        if args.command == "status":
            from cli.commands.status import status_command

            status_command(args.watch, args.interval, not args.no_auto_retry)
        elif args.command == "start":
            from cli.commands.start import start_command

            start_command(
                args.agent,
                args.prompt,
                args.max_retries,
                args.auto_retry,
                args.priority,
                args.timeout,
            )
        elif args.command == "run":
            from cli.commands.run import run_command

            run_command(args.parallel)
        elif args.command == "cancel":
            from cli.commands.cancel import cancel_command

            cancel_command(args.task_id)
        elif args.command == "retry":
            from cli.commands.retry import retry_command

            retry_command(args.task_id, args.max_retries, args.auto)
        elif args.command == "clean":
            from cli.commands.clean import clean_command

            clean_command(args.filter, args.yes)
        elif args.command == "timeout":
            from cli.commands.timeout_cmd import timeout_command

            timeout_command(args.subcommand, *args.args)
        else:
            console.print(f"[red]Unknown command: {args.command}[/red]", "red")
            parser.print_help()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]", "red")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
