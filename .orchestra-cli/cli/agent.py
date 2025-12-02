"""Minimal CLI implementation using only Python stdlib.

This is a simplified version that doesn't require Click or Rich.
It provides the same functionality with basic formatting.
"""

import argparse
import sys
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
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug logging (or set AGENT_DEBUG=1)",
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
    start_parser.add_argument(
        "--depends-on",
        nargs="+",
        metavar="TASK_ID",
        help="Task IDs this task depends on"
    )

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

    # Daemon command
    daemon_parser = subparsers.add_parser("daemon", help="Run in daemon mode")
    daemon_parser.add_argument(
        "--max-concurrent", "-c", type=int, default=3, help="Max concurrent tasks"
    )
    daemon_parser.add_argument(
        "--interval", "-i", type=int, default=5, help="Check interval in seconds"
    )

    # Archive command
    archive_parser = subparsers.add_parser("archive", help="Archive old tasks")
    archive_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be archived"
    )
    archive_parser.add_argument(
        "--force", "-f", action="store_true", help="Archive even if disabled in config"
    )

    # Archive stats subcommand
    archive_subparsers = archive_parser.add_subparsers(dest="archive_subcommand")
    archive_subparsers.add_parser("stats", help="Show archive statistics")

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_subcommand")
    config_subparsers.add_parser("init", help="Create default config file")
    config_subparsers.add_parser("show", help="Show current configuration")
    config_set_parser = config_subparsers.add_parser("set", help="Set config value")
    config_set_parser.add_argument("key", help="Config key (e.g., archive.enabled)")
    config_set_parser.add_argument("value", help="Value to set")

    # Deps command
    deps_parser = subparsers.add_parser("deps", help="Manage task dependencies")
    deps_subparsers = deps_parser.add_subparsers(dest="deps_subcommand")
    deps_show_parser = deps_subparsers.add_parser("show", help="Show task dependencies")
    deps_show_parser.add_argument("task_id", help="Task ID to show dependencies for")
    deps_subparsers.add_parser("graph", help="Show full dependency graph")
    deps_subparsers.add_parser("validate", help="Validate dependency graph for cycles")

    # Index command
    index_parser = subparsers.add_parser("index", help="Manage task index")
    index_subparsers = index_parser.add_subparsers(dest="index_subcommand")
    index_subparsers.add_parser("rebuild", help="Rebuild task index")
    index_subparsers.add_parser("stats", help="Show index statistics")
    index_subparsers.add_parser("verify", help="Verify index consistency")

    args = parser.parse_args()

    # Enable debug logging if --debug flag is passed
    if args.debug:
        from cli.utils.logger import set_debug

        set_debug(True)

    if args.version:
        console.print("[bold]OpenCode Agent Orchestrator[/bold] v2.2.0", "bold")
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
                args.depends_on,
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
        elif args.command == "daemon":
            from cli.commands.daemon import daemon_command

            daemon_command(args.max_concurrent, args.interval)
        elif args.command == "archive":
            if args.archive_subcommand == "stats":
                from cli.commands.archive import archive_stats_command

                archive_stats_command()
            else:
                from cli.commands.archive import archive_command

                archive_command(args.dry_run, args.force)
        elif args.command == "config":
            if args.config_subcommand == "init":
                from cli.commands.config_cmd import config_init_command

                config_init_command()
            elif args.config_subcommand == "show":
                from cli.commands.config_cmd import config_show_command

                config_show_command()
            elif args.config_subcommand == "set":
                from cli.commands.config_cmd import config_set_command

                config_set_command(args.key, args.value)
            else:
                console.print("[yellow]Use: config init|show|set[/yellow]")
        elif args.command == "deps":
            if args.deps_subcommand == "show":
                from cli.commands.deps import deps_show_command

                deps_show_command(args.task_id)
            elif args.deps_subcommand == "graph":
                from cli.commands.deps import deps_graph_command

                deps_graph_command()
            elif args.deps_subcommand == "validate":
                from cli.commands.deps import deps_validate_command

                sys.exit(deps_validate_command())
            else:
                console.print("[yellow]Use: deps show|graph|validate[/yellow]")
        elif args.command == "index":
            if args.index_subcommand == "rebuild":
                from cli.commands.index_cmd import index_rebuild_command

                index_rebuild_command()
            elif args.index_subcommand == "stats":
                from cli.commands.index_cmd import index_stats_command

                index_stats_command()
            elif args.index_subcommand == "verify":
                from cli.commands.index_cmd import index_verify_command

                sys.exit(index_verify_command())
            else:
                console.print("[yellow]Use: index rebuild|stats|verify[/yellow]")
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
