"""Archive command implementation."""

import sys
from datetime import datetime
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.repository import TaskRepository
from cli.core.archive_manager import ArchiveManager
from cli.core.config import OrchestratorConfig


def archive_command(dry_run: bool = False, force: bool = False):
    """
    Archive old completed/failed tasks.

    Args:
        dry_run: Show what would be archived without doing it
        force: Archive even if auto-archival is disabled
    """
    repo = TaskRepository()
    config = OrchestratorConfig.load()

    if not config.archive.enabled and not force:
        print("Auto-archival is disabled. Use --force to archive anyway.")
        print("To enable: set archive.enabled=true in .orchestra/config.json")
        print("\nTo create a default config file, run:")
        print("  python3 -m cli config init")
        return

    manager = ArchiveManager(repo, config)
    tasks = manager.get_archivable_tasks()

    if not tasks:
        print("No tasks eligible for archival.")
        print(
            f"\nCompleted tasks older than {config.archive.max_completed_age_days} days"
        )
        print(f"Failed tasks older than {config.archive.max_failed_age_days} days")
        return

    print(f"Found {len(tasks)} task(s) eligible for archival:\n")
    for task in tasks:
        age = (datetime.now() - (task.completedAt or task.createdAt)).days
        print(f"  {task.taskId} ({task.status.value}, {age} days old)")

    if dry_run:
        print("\n[Dry run - no changes made]")
        return

    # Confirm if more than 10 tasks
    if len(tasks) > 10:
        response = input(f"\nArchive {len(tasks)} tasks? (y/N): ")
        if response.lower() != "y":
            print("Cancelled.")
            return

    archived, errors = manager.run_archival()
    print(f"\nArchived: {archived}, Errors: {errors}")

    # Show archive stats
    stats = manager.get_archive_stats()
    print(f"Archive contains {stats['total']} tasks ({stats['size_mb']:.2f} MB)")


def archive_stats_command():
    """Show archive statistics."""
    repo = TaskRepository()
    config = OrchestratorConfig.load()
    manager = ArchiveManager(repo, config)

    stats = manager.get_archive_stats()
    print(f"\nArchive Statistics:")
    print(f"  Total archived tasks: {stats['total']}")
    print(f"  Total size: {stats['size_mb']:.2f} MB")
    print(f"  Location: {manager.archive_dir}")

    if config.archive.enabled:
        print(f"\nAuto-archival: ENABLED")
        print(
            f"  Completed tasks: archived after {config.archive.max_completed_age_days} days"
        )
        print(
            f"  Failed tasks: archived after {config.archive.max_failed_age_days} days"
        )
        print(f"  Queue size limit: {config.archive.max_queue_size} tasks")
    else:
        print(f"\nAuto-archival: DISABLED")
        print(f"  To enable, run: python3 -m cli config set archive.enabled true")

