"""Index management commands."""

import sys
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.repository import TaskRepository
from cli.core.index import TaskIndex


def index_rebuild_command():
    """Rebuild the task index from scratch."""
    print("Rebuilding task index...")
    
    repo = TaskRepository()
    index = TaskIndex()
    
    tasks = repo.load_all()
    index.rebuild(tasks)
    
    print(f"\033[92m✓ Index rebuilt with {len(tasks)} tasks\033[0m")


def index_stats_command():
    """Show index statistics."""
    index = TaskIndex()
    
    print("\n\033[1mTask Index Statistics:\033[0m")
    print(f"  Total tasks: {index.data['count']}")
    print(f"  Last updated: {index.data.get('last_updated', 'Never')}")
    
    print(f"\n\033[1mBy Status:\033[0m")
    for status, task_ids in sorted(index.data["by_status"].items()):
        print(f"  {status}: {len(task_ids)}")
    
    print(f"\n\033[1mBy Agent:\033[0m")
    for agent, task_ids in sorted(index.data["by_agent"].items()):
        print(f"  {agent}: {len(task_ids)}")
    
    print(f"\n\033[1mBy Priority:\033[0m")
    for priority, task_ids in sorted(index.data["by_priority"].items(), key=lambda x: int(x[0]), reverse=True):
        print(f"  Priority {priority}: {len(task_ids)}")


def index_verify_command():
    """Verify index consistency with actual tasks."""
    print("Verifying index consistency...")
    
    repo = TaskRepository()
    index = TaskIndex()
    
    tasks = repo.load_all()
    actual_ids = {t.taskId for t in tasks}
    
    # Get all IDs from index
    indexed_ids = set()
    for status_list in index.data["by_status"].values():
        indexed_ids.update(status_list)
    
    # Find discrepancies
    missing_from_index = actual_ids - indexed_ids
    extra_in_index = indexed_ids - actual_ids
    
    if not missing_from_index and not extra_in_index:
        print("\033[92m✓ Index is consistent\033[0m")
        return 0
    
    if missing_from_index:
        print(f"\033[93m⚠ {len(missing_from_index)} tasks missing from index:\033[0m")
        for task_id in list(missing_from_index)[:5]:
            print(f"  - {task_id}")
        if len(missing_from_index) > 5:
            print(f"  ... and {len(missing_from_index) - 5} more")
    
    if extra_in_index:
        print(f"\033[93m⚠ {len(extra_in_index)} extra tasks in index:\033[0m")
        for task_id in list(extra_in_index)[:5]:
            print(f"  - {task_id}")
        if len(extra_in_index) > 5:
            print(f"  ... and {len(extra_in_index) - 5} more")
    
    print("\nRun 'python3 -m cli index rebuild' to fix inconsistencies")
    return 1

