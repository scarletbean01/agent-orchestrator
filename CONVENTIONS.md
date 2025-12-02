# Coding Conventions

This document outlines the coding conventions, style guides, and best practices for the Agent Orchestrator project.

## General Principles

- **Simplicity**: Prefer simple, straightforward solutions over complex abstractions
- **Pure Python stdlib**: No external dependencies beyond Python standard library (except Pydantic for models)
- **Cross-platform**: Code must work on Windows, macOS, and Linux
- **Performance**: Optimize for fast execution (<100ms for most operations)
- **Maintainability**: Write clear, self-documenting code with appropriate comments

## Python Style Guide

### Version Support
- **Target**: Python 3.7+
- **Recommended**: Python 3.10+
- **Tested with**: Python 3.13

### Code Style
- Follow **PEP 8** style guide
- Use **type hints** for all function parameters and return values
- Maximum line length: **88 characters** (Black formatter standard)
- Use **double quotes** for strings (consistent with Black)

### Imports
```python
# Standard library imports first
import sys
import json
from pathlib import Path
from typing import Optional, List

# Third-party imports (minimal - only Pydantic for models)
from pydantic import BaseModel

# Local imports last
from cli.utils.logger import logger
from cli.core.models import Task
```

### Naming Conventions
- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`
- **Module-level privates**: `_single_underscore`

### Docstrings
- Use **triple-quoted strings** for all docstrings
- Follow **Google style** for docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function.

    Longer description if needed. Can span multiple lines.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When X happens
    """
    pass
```

## Project Structure

### Directory Organization
```
.orchestra-cli/
├── cli/                    # Main CLI package
│   ├── agent.py            # CLI entry point
│   ├── commands/           # Command implementations (one file per command)
│   ├── core/               # Core business logic
│   │   ├── models.py       # Data models (Pydantic)
│   │   ├── repository.py   # Data persistence layer
│   │   ├── reconciler.py   # State reconciliation
│   │   ├── scheduler.py    # Task scheduling
│   │   ├── executor.py     # Process execution
│   │   └── formatter.py    # Output formatting
│   └── utils/              # Utility modules
│       ├── logger.py       # Logging utilities
│       ├── process.py      # Process management
│       ├── paths.py        # Path constants
│       └── time_utils.py   # Time utilities
├── prompts/                # Prompt templates
├── command/                # LLM slash commands
├── agent/                  # Sub-agent definitions
└── scripts/                # Helper scripts and tests
```

### Module Responsibilities
- **`commands/`**: CLI command handlers - thin wrappers that call core logic
- **`core/`**: Business logic - no CLI/UI concerns
- **`utils/`**: Reusable utilities - stateless helper functions
- **`models.py`**: Data structures only - no business logic

## Code Patterns

### Error Handling
```python
# Use specific exceptions
try:
    task = repository.load_task(task_id)
except FileNotFoundError:
    logger.error(f"Task {task_id} not found")
    return
except json.JSONDecodeError as e:
    logger.error(f"Invalid task JSON: {e}")
    return

# Log errors with context
logger.error(f"Failed to launch task {task.taskId}: {e}")
```

### File Operations
```python
# Use pathlib.Path for all file operations
from pathlib import Path

task_file = TASKS_DIR / f"{task_id}.json"

# Atomic writes for JSON
temp_file = task_file.with_suffix('.json.tmp')
temp_file.write_text(json.dumps(data, indent=2))
temp_file.rename(task_file)

# Always use context managers
with open(file_path, 'r') as f:
    data = json.load(f)
```

### Logging
```python
from cli.utils.logger import logger

# Use appropriate log levels
logger.debug("Detailed debugging info")  # Only shown with --debug
logger.info("Task lifecycle events")     # Always shown
logger.warning("Recoverable issues")     # Always shown
logger.error("Critical failures")        # Always shown

# Include context in logs
logger.info(f"Task {task.taskId} started (PID: {pid})")
```

### Process Management
```python
import subprocess
from cli.utils.process import is_process_alive, kill_process

# Cross-platform process checks
if is_process_alive(pid):
    logger.info(f"Process {pid} is running")

# Cross-platform process termination
kill_process(pid, timeout=5)
```

### Time Handling
```python
from datetime import datetime, timezone

# Always use UTC
now = datetime.now(timezone.utc)

# ISO 8601 format for serialization
timestamp = now.isoformat()

# Parse ISO 8601
parsed = datetime.fromisoformat(timestamp)
```

## Testing

### Test Structure
- Place tests in `.orchestra-cli/tests/`
- Name test files `test_<module>.py`
- Use pytest for test framework
- Mock external dependencies (subprocess, file I/O)

### Test Conventions
```python
import pytest
from cli.core.models import Task, TaskStatus

def test_task_creation():
    """Test basic task creation."""
    task = Task(
        taskId="task_123",
        status=TaskStatus.PENDING,
        agent="coder",
        prompt="Test prompt",
        planFile=".orchestra/plans/task_123_plan.md",
        logFile=".orchestra/logs/task_123.log",
        createdAt=datetime.now(timezone.utc)
    )
    assert task.taskId == "task_123"
    assert task.status == TaskStatus.PENDING
```

## Git Workflow

### Commit Messages
Follow **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build/tooling changes

**Examples:**
```
feat(executor): add prompt template support for external agents

Implements prompt template loading and variable substitution
for agents like Augment that don't support subagent configs.

Closes #42
```

```
fix(reconciler): handle missing PID in running tasks

Some tasks may have status=running but no PID recorded.
Handle this case gracefully and mark as failed.
```

### Branch Naming
- `feat/<feature-name>` - New features
- `fix/<bug-description>` - Bug fixes
- `docs/<what-changed>` - Documentation updates
- `refactor/<component>` - Code refactoring

## Documentation

### Code Comments
- Write comments for **why**, not **what**
- Use `# TODO:` for future work
- Use `# FIXME:` for known issues
- Use `# NOTE:` for important clarifications

```python
# TODO: Implement priority-based scheduling (currently FIFO only)
# FIXME: Race condition possible if two processes write simultaneously
# NOTE: Windows uses different process creation flags than POSIX
```

### README Updates
- Keep README.md in sync with actual code
- Update examples when command syntax changes
- Document all environment variables
- Include troubleshooting section

### API Documentation
- Document all public functions/classes
- Include usage examples in docstrings
- Keep type hints accurate

## Performance Guidelines

### File I/O
- Use atomic writes for critical files (tasks JSON)
- Avoid unnecessary file reads (cache when appropriate)
- Use `Path.exists()` instead of try/except for existence checks

### Process Management
- Launch processes asynchronously
- Don't block on process completion
- Use sentinel files for completion detection

### Memory Usage
- Don't load all tasks into memory at once
- Stream large log files
- Clean up completed tasks periodically

## Security Considerations

### Input Validation
- Validate task IDs match expected format
- Sanitize user prompts before passing to shell
- Check file paths don't escape `.orchestra/` directory

### Process Isolation
- Run agent processes with proper isolation
- Don't trust agent output blindly
- Validate sentinel files before trusting completion status

### Credentials
- Never log sensitive information
- Don't commit API keys or credentials
- Use environment variables for secrets

## Cross-Platform Guidelines

### Path Handling
```python
# Always use pathlib.Path
from pathlib import Path

# Good
config_path = Path(".orchestra-cli") / "agent-config.json"

# Bad
config_path = ".orchestra-cli/agent-config.json"  # Won't work on Windows
```

### Process Management
```python
# Use platform-specific helpers
from cli.utils.process import get_os_name

if get_os_name() == "windows":
    # Windows-specific code
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
else:
    # POSIX-specific code
    start_new_session = True
```

### Shell Commands
- Avoid shell commands when possible
- Use subprocess module with proper escaping
- Test on all platforms (Windows, macOS, Linux)

## Error Messages

### User-Facing Errors
- Be specific about what went wrong
- Suggest corrective action
- Include relevant context (task ID, file path)

```python
# Good
logger.error(f"Task {task_id} not found in .orchestra/tasks/")
logger.info("Run 'python -m cli status' to see available tasks")

# Bad
logger.error("Task not found")
```

### Debug Information
- Include full context in debug logs
- Log command arrays, not just strings
- Show variable values at key points

## Version Compatibility

### Breaking Changes
- Document in CHANGELOG.md
- Provide migration guide
- Support both old and new formats during transition

### Backward Compatibility
- Maintain file format compatibility when possible
- Support old sentinel file formats
- Add deprecation warnings for removed features

## Tools and Linters

### Recommended Tools
- **Formatter**: Black (88 char line length)
- **Linter**: Ruff (fast Python linter)
- **Type checker**: mypy (optional but recommended)
- **Import sorting**: isort

### Configuration Files
Add to project root:

**`pyproject.toml`:**
```toml
[tool.black]
line-length = 88
target-version = ['py37']

[tool.isort]
profile = "black"
line_length = 88

[tool.ruff]
line-length = 88
target-version = "py37"
```

## Summary Checklist

Before submitting code, verify:

- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have type hints
- [ ] Docstrings present for public APIs
- [ ] Tests pass on all platforms
- [ ] No external dependencies added (except approved)
- [ ] Error messages are user-friendly
- [ ] Logging uses appropriate levels
- [ ] File operations are atomic where needed
- [ ] Cross-platform compatibility verified
- [ ] Documentation updated if needed
- [ ] Commit message follows convention
- [ ] No secrets or credentials committed

---

*These conventions ensure code quality, maintainability, and consistency across the Agent Orchestrator project.*
