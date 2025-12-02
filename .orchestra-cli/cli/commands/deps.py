"""Dependency management commands."""

import sys
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.repository import TaskRepository
from cli.core.dependency_resolver import DependencyResolver
from cli.core.models import TaskStatus


def deps_show_command(task_id: str):
    """Show dependencies for a task."""
    repo = TaskRepository()
    task = repo.load(task_id)

    if not task:
        print(f"\033[91mError: Task {task_id} not found\033[0m")
        return

    print(f"\n\033[1mTask: {task_id}\033[0m")
    print(f"Status: {task.status.value}")

    if task.dependsOn:
        print(f"\n\033[1mDependencies ({len(task.dependsOn)}):\033[0m")
        for dep_id in task.dependsOn:
            dep_task = repo.load(dep_id)
            if dep_task:
                status_icon = "✓" if dep_task.status == TaskStatus.COMPLETE else "⏸"
                print(f"  {status_icon} {dep_id} ({dep_task.status.value})")
            else:
                print(f"  ✗ {dep_id} (not found)")
    else:
        print("\nNo dependencies")

    if task.is_blocked:
        print(f"\n\033[93m⚠ Task is blocked: {task.blockedReason}\033[0m")


def deps_graph_command():
    """Show dependency graph for all tasks."""
    repo = TaskRepository()
    resolver = DependencyResolver(repo)

    graph = resolver.build_dependency_graph()

    if not graph:
        print("No tasks with dependencies found")
        return

    print("\n\033[1mDependency Graph:\033[0m\n")
    for task_id, deps in sorted(graph.items()):
        task = repo.load(task_id)
        if task and deps:
            status = task.status.value
            print(f"{task_id} ({status})")
            for dep_id in sorted(deps):
                dep_task = repo.load(dep_id)
                dep_status = dep_task.status.value if dep_task else "missing"
                print(f"  └─> {dep_id} ({dep_status})")
            print()


def deps_validate_command():
    """Validate dependency graph for cycles."""
    repo = TaskRepository()
    resolver = DependencyResolver(repo)

    cycle = resolver.detect_cycle()

    if cycle:
        print("\033[91m✗ Circular dependency detected!\033[0m")
        print(f"\nCycle: {' -> '.join(cycle)}")
        return 1
    else:
        print("\033[92m✓ No circular dependencies found\033[0m")
        return 0

