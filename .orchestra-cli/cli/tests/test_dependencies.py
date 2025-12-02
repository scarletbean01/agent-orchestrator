"""Tests for dependency resolver."""

import sys
from pathlib import Path

# Ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.dependency_resolver import DependencyResolver
from cli.core.models import Task, TaskStatus


class TestDependencyResolver:
    """Test cases for DependencyResolver."""

    def test_build_dependency_graph(self, repo, sample_task):
        """Should build dependency graph."""
        task1 = sample_task.model_copy()
        task1.taskId = "task_1"
        task1.dependsOn = []
        
        task2 = sample_task.model_copy()
        task2.taskId = "task_2"
        task2.dependsOn = ["task_1"]
        
        repo.save(task1)
        repo.save(task2)
        
        resolver = DependencyResolver(repo)
        graph = resolver.build_dependency_graph()
        
        assert "task_2" in graph
        assert "task_1" in graph["task_2"]

    def test_detect_cycle_no_cycle(self, repo, sample_task):
        """Should not detect cycle in valid graph."""
        task1 = sample_task.model_copy()
        task1.taskId = "task_1"
        task1.dependsOn = []
        
        task2 = sample_task.model_copy()
        task2.taskId = "task_2"
        task2.dependsOn = ["task_1"]
        
        repo.save(task1)
        repo.save(task2)
        
        resolver = DependencyResolver(repo)
        cycle = resolver.detect_cycle()
        
        assert cycle is None

    def test_detect_cycle_simple(self, repo, sample_task):
        """Should detect simple cycle."""
        task1 = sample_task.model_copy()
        task1.taskId = "task_1"
        task1.dependsOn = ["task_2"]
        
        task2 = sample_task.model_copy()
        task2.taskId = "task_2"
        task2.dependsOn = ["task_1"]
        
        repo.save(task1)
        repo.save(task2)
        
        resolver = DependencyResolver(repo)
        cycle = resolver.detect_cycle()
        
        assert cycle is not None
        assert len(cycle) >= 2

    def test_get_ready_tasks_no_deps(self, repo, sample_task):
        """Should return tasks with no dependencies."""
        task = sample_task.model_copy()
        task.taskId = "task_1"
        task.dependsOn = []
        
        repo.save(task)
        
        resolver = DependencyResolver(repo)
        ready = resolver.get_ready_tasks()
        
        assert len(ready) == 1
        assert ready[0].taskId == "task_1"

    def test_get_ready_tasks_satisfied_deps(self, repo, sample_task, completed_task):
        """Should return tasks with satisfied dependencies."""
        task1 = completed_task.model_copy()
        task1.taskId = "task_1"
        task1.status = TaskStatus.COMPLETE
        task1.dependsOn = []
        
        task2 = sample_task.model_copy()
        task2.taskId = "task_2"
        task2.dependsOn = ["task_1"]
        
        repo.save(task1)
        repo.save(task2)
        
        resolver = DependencyResolver(repo)
        ready = resolver.get_ready_tasks()
        
        assert len(ready) == 1
        assert ready[0].taskId == "task_2"

    def test_get_ready_tasks_unsatisfied_deps(self, repo, sample_task):
        """Should not return tasks with unsatisfied dependencies."""
        task1 = sample_task.model_copy()
        task1.taskId = "task_1"
        task1.status = TaskStatus.PENDING
        task1.dependsOn = []
        
        task2 = sample_task.model_copy()
        task2.taskId = "task_2"
        task2.dependsOn = ["task_1"]
        
        repo.save(task1)
        repo.save(task2)
        
        resolver = DependencyResolver(repo)
        ready = resolver.get_ready_tasks()
        
        # Only task_1 should be ready
        assert len(ready) == 1
        assert ready[0].taskId == "task_1"

    def test_validate_new_dependency_valid(self, repo):
        """Should validate valid dependency."""
        resolver = DependencyResolver(repo)
        valid, msg = resolver.validate_new_dependency("task_2", ["task_1"])
        assert valid is True

    def test_validate_new_dependency_cycle(self, repo, sample_task):
        """Should reject dependency that creates cycle."""
        task1 = sample_task.model_copy()
        task1.taskId = "task_1"
        task1.dependsOn = ["task_2"]
        
        repo.save(task1)
        
        resolver = DependencyResolver(repo)
        valid, msg = resolver.validate_new_dependency("task_2", ["task_1"])
        assert valid is False
        assert "cycle" in msg.lower()

