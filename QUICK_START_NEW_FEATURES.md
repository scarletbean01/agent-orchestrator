# Quick Start: New Features Guide

This guide covers the new features added to the Agent Orchestrator in v3.0.

## 🗄️ Auto-Archival

### Setup

```bash
# 1. Create configuration file
python3 -m cli config init

# 2. Enable archival
python3 -m cli config set archive.enabled true

# 3. Configure retention (optional)
python3 -m cli config set archive.max_completed_age_days 7
python3 -m cli config set archive.max_failed_age_days 14
python3 -m cli config set archive.max_queue_size 100
```

### Usage

```bash
# Preview what would be archived
python3 -m cli archive --dry-run

# Archive old tasks
python3 -m cli archive

# View archive statistics
python3 -m cli archive stats

# View current configuration
python3 -m cli config show
```

### Automatic Archival

When running in daemon mode, archival runs automatically every hour:

```bash
python3 -m cli daemon --max-concurrent 3
# Daemon will automatically archive old tasks based on config
```

---

## 🔗 Task Dependencies

### Creating Dependent Tasks

```bash
# Create base task
python3 -m cli start coder "Setup database schema"
# Output: Task task_1733123456789 created

# Create dependent task
python3 -m cli start coder "Seed initial data" --depends-on task_1733123456789

# Create task with multiple dependencies
python3 -m cli start coder "Run tests" --depends-on task_123 task_456 task_789
```

### Viewing Dependencies

```bash
# Show dependencies for a specific task
python3 -m cli deps show task_123

# Show full dependency graph
python3 -m cli deps graph

# Validate for circular dependencies
python3 -m cli deps validate
```

### How It Works

1. Tasks with unsatisfied dependencies are **blocked**
2. Blocked tasks show 🚫 icon in status
3. Scheduler only runs tasks with satisfied dependencies
4. If a dependency fails, dependent tasks are blocked
5. Dependencies are checked in priority order

### Example Workflow

```bash
# Create a pipeline
python3 -m cli start coder "Task 1: Setup" --priority 10
python3 -m cli start coder "Task 2: Build" --depends-on task_1 --priority 9
python3 -m cli start coder "Task 3: Test" --depends-on task_2 --priority 8
python3 -m cli start coder "Task 4: Deploy" --depends-on task_3 --priority 7

# Run in parallel - they execute in dependency order
python3 -m cli run --parallel 4

# Check status
python3 -m cli status
```

---

## 🧪 Unit Tests

### Running Tests

```bash
# Unix/Linux/macOS
cd .orchestra-cli
chmod +x run-tests.sh
./run-tests.sh

# Windows PowerShell
cd .orchestra-cli
.\run-tests.ps1

# Direct pytest
cd .orchestra-cli
pytest cli/tests/ -v
```

### Test Coverage

The test suite covers:
- ✅ Task models and properties
- ✅ Repository CRUD operations
- ✅ Scheduler priority and FIFO ordering
- ✅ Dependency resolution and cycle detection
- ✅ Blocked task handling

### Adding New Tests

```python
# cli/tests/test_my_feature.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.core.models import Task

def test_my_feature(repo, sample_task):
    """Test description."""
    # Your test code here
    assert True
```

---

## ⚡ Performance Index

### When to Use

Use the index for large task queues (100+ tasks) to speed up queries.

### Commands

```bash
# Rebuild index from scratch
python3 -m cli index rebuild

# View index statistics
python3 -m cli index stats

# Verify index consistency
python3 -m cli index verify
```

### Index Structure

The index provides O(1) lookups for:
- Tasks by status (pending, running, complete, failed)
- Tasks by agent (coder, auggie, etc.)
- Tasks by priority (1-10)

### Automatic Maintenance

The index is automatically updated when:
- Creating new tasks
- Updating task status
- Deleting tasks

---

## 🎯 Complete Example: Production Workflow

```bash
# 1. Setup configuration
python3 -m cli config init
python3 -m cli config set archive.enabled true
python3 -m cli config set archive.max_completed_age_days 7

# 2. Create a task pipeline with dependencies
python3 -m cli start coder "Setup infrastructure" --priority 10
# task_1 created

python3 -m cli start coder "Deploy backend" --depends-on task_1 --priority 9
# task_2 created

python3 -m cli start coder "Deploy frontend" --depends-on task_1 --priority 9
# task_3 created

python3 -m cli start coder "Run integration tests" --depends-on task_2 task_3 --priority 8
# task_4 created

# 3. Validate dependency graph
python3 -m cli deps validate
# ✓ No circular dependencies found

python3 -m cli deps graph
# Shows the full dependency tree

# 4. Start daemon for automatic execution
python3 -m cli daemon --max-concurrent 2 --interval 5
# Daemon will:
# - Execute tasks in dependency order
# - Respect concurrency limits
# - Auto-retry failed tasks (if enabled)
# - Archive old tasks every hour

# 5. Monitor progress (in another terminal)
python3 -m cli status --watch

# 6. Check archive statistics
python3 -m cli archive stats
```

---

## 🔍 Troubleshooting

### Circular Dependency Detected

```bash
python3 -m cli deps validate
# ✗ Circular dependency detected!
# Cycle: task_1 -> task_2 -> task_1

# Fix: Remove one of the dependencies
```

### Index Out of Sync

```bash
python3 -m cli index verify
# ⚠ 5 tasks missing from index

python3 -m cli index rebuild
# ✓ Index rebuilt with 42 tasks
```

### Archive Not Working

```bash
python3 -m cli config show
# Check if archive.enabled is true

python3 -m cli archive --dry-run
# Preview what would be archived

python3 -m cli archive --force
# Force archival even if disabled
```

---

## 📚 Additional Resources

- **Full Documentation**: See `AGENTS.md` for complete feature documentation
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md` for technical details
- **Prompt Templates**: See `PROMPT_TEMPLATES.md` for agent integration
- **Conventions**: See `CONVENTIONS.md` for coding standards

---

**Version**: 3.0  
**Last Updated**: December 2, 2025

