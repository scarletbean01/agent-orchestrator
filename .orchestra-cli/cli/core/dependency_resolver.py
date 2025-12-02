"""Task dependency resolution and DAG validation."""

import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task, TaskStatus
from cli.core.repository import TaskRepository
from cli.utils.logger import logger


class DependencyResolver:
    """Resolves task dependencies and detects cycles."""

    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build a dependency graph from all tasks."""
        graph = defaultdict(set)
        for task in self.repo.load_all():
            for dep_id in task.dependsOn:
                graph[task.taskId].add(dep_id)
        return graph

    def detect_cycle(self, new_task_id: Optional[str] = None, new_deps: Optional[List[str]] = None) -> Optional[List[str]]:
        """
        Detect circular dependencies. Returns cycle path or None.
        
        Args:
            new_task_id: Optional task ID to test (for validation before adding)
            new_deps: Optional dependencies for the new task
        """
        graph = self.build_dependency_graph()
        
        # Add temporary dependency if testing
        if new_task_id and new_deps:
            for dep in new_deps:
                graph[new_task_id].add(dep)
        
        visited = set()
        path = []

        def dfs(node: str) -> Optional[List[str]]:
            if node in path:
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]
            if node in visited:
                return None

            path.append(node)
            for dep in graph.get(node, []):
                result = dfs(dep)
                if result:
                    return result
            path.pop()
            visited.add(node)
            return None

        for task_id in graph:
            result = dfs(task_id)
            if result:
                return result
        return None

    def get_ready_tasks(self) -> List[Task]:
        """Get tasks whose dependencies are all satisfied."""
        ready = []
        all_tasks = {t.taskId: t for t in self.repo.load_all()}

        for task in all_tasks.values():
            if task.status != TaskStatus.PENDING:
                continue

            # Skip if already blocked
            if task.is_blocked:
                continue

            # Check all dependencies
            deps_satisfied = True
            blocking_task = None

            for dep_id in task.dependsOn:
                dep_task = all_tasks.get(dep_id)
                if not dep_task:
                    logger.warning(
                        f"Task {task.taskId} depends on missing task {dep_id}"
                    )
                    task.blockedBy = dep_id
                    task.blockedReason = f"Dependency {dep_id} not found"
                    self.repo.save(task)
                    deps_satisfied = False
                    break

                if dep_task.status == TaskStatus.COMPLETE:
                    continue
                elif dep_task.status == TaskStatus.FAILED:
                    # Dependency failed - mark this task as blocked
                    task.blockedBy = dep_id
                    task.blockedReason = f"Dependency {dep_id} failed"
                    self.repo.save(task)
                    deps_satisfied = False
                    break
                elif dep_task.status == TaskStatus.CANCELLED:
                    # Dependency cancelled - mark this task as blocked
                    task.blockedBy = dep_id
                    task.blockedReason = f"Dependency {dep_id} cancelled"
                    self.repo.save(task)
                    deps_satisfied = False
                    break
                else:
                    # Dependency not yet complete
                    deps_satisfied = False
                    blocking_task = dep_id
                    break

            if deps_satisfied:
                ready.append(task)

        return ready

    def validate_new_dependency(
        self, task_id: str, depends_on: List[str]
    ) -> Tuple[bool, str]:
        """Validate adding new dependencies won't create a cycle."""
        cycle = self.detect_cycle(task_id, depends_on)
        if cycle:
            return False, f"Adding dependency would create a cycle: {' -> '.join(cycle)}"
        return True, "OK"

    def get_dependency_chain(self, task_id: str) -> List[str]:
        """Get the full dependency chain for a task."""
        all_tasks = {t.taskId: t for t in self.repo.load_all()}
        task = all_tasks.get(task_id)
        if not task:
            return []

        chain = []
        visited = set()

        def traverse(tid: str):
            if tid in visited:
                return
            visited.add(tid)
            t = all_tasks.get(tid)
            if t:
                for dep in t.dependsOn:
                    traverse(dep)
                    chain.append(dep)

        traverse(task_id)
        return chain

