# OpenCode Agent Orchestrator Framework v3.0

This document describes the file-system-based agent orchestration framework with a pure Python CLI and specialized sub-agents.

## 🚀 What's New in v3.0

**Version 3.0** adds major new features while maintaining the pure Python CLI architecture.

### Key Changes (v3.0)
- 🗄️ **Auto-Archival System**: Automatic cleanup of old tasks with configurable retention policies
- 🔗 **Task Dependencies**: Full DAG execution with cycle detection and dependency resolution
- 🧪 **Unit Tests**: Comprehensive test coverage for all core modules
- ⚡ **Performance Index**: Fast lookups for large task queues (100+ tasks)
- 📝 **Updated Documentation**: Complete documentation of all features
- 🔧 **Configuration Management**: JSON-based configuration system

### Key Features (v2.0-v3.0)
- ⚡ **20-50x faster**: Commands execute in <100ms with pure Python
- 🔧 **Zero dependencies**: Pure Python stdlib (no pip install required)
- 🎨 **Rich output**: ANSI colors, formatted tables, status icons
- ✅ **All features**: Status, start, run, cancel, retry, clean, timeout, archive, config, deps, index commands
- 🪟 **Full Windows support**: Native cross-platform (Windows/macOS/Linux)
- 🔌 **Agent decoupling**: Use any CLI tool (OpenCode, Augment, Cursor) via config file
- 📝 **Prompt Templates**: Inject orchestration protocol into any agent (Augment, Cursor, etc.)
- 🔧 **Debug Logging**: Switchable via `--debug` flag or `AGENT_DEBUG=1` environment variable
- 🪟 **Windows Escaping**: Platform-specific newline escaping for shell compatibility
- 🎨 **Colored Output**: Color-coded log levels (DEBUG=gray, INFO=green, WARNING=yellow, ERROR=red)
- 🗄️ **Auto-Archival**: Automatic cleanup with configurable retention policies
- 🔗 **Task Dependencies**: DAG execution with cycle detection
- 🧪 **Test Coverage**: 30+ unit tests for core modules
- ⚡ **Performance Index**: O(1) lookups by status/agent/priority

### Quick Start (v3.0)

```bash
# Setup environment (required)
export PYTHONPATH=.orchestra-cli:$PYTHONPATH

# Initialize configuration (optional but recommended)
python3 -m cli config init
python3 -m cli config set archive.enabled true

# Basic usage
python3 -m cli status --watch
python3 -m cli start coder "Create a web server" --timeout 300
python3 -m cli run --parallel 3

# Task dependencies
python3 -m cli start coder "Setup DB" --priority 10
python3 -m cli start coder "Deploy API" --depends-on task_1 --priority 9

# Daemon mode with auto-archival
python3 -m cli daemon --max-concurrent 3 --interval 5

# Enable debug logging for troubleshooting
python3 -m cli --debug run

# Create an alias for convenience (optional)
alias agent='PYTHONPATH=.orchestra-cli:$PYTHONPATH python3 -m cli'
agent status
agent start coder "Build a feature"
```

## What's New in v3.0 - Feature Summary

### 🗄️ Auto-Archival System
Automatically clean up old tasks with configurable retention policies. No more manual cleanup!

- **Configuration-driven**: Set retention periods for completed vs failed tasks
- **Daemon integration**: Automatic archival every hour in daemon mode
- **Archive statistics**: Track archived tasks and storage usage
- **Manual control**: Archive on-demand with dry-run preview

### 🔗 Task Dependencies
Create complex workflows with task dependencies and DAG execution.

- **Dependency declaration**: `--depends-on task_1 task_2` when creating tasks
- **Cycle detection**: Prevents circular dependencies
- **Smart scheduling**: Only runs tasks with satisfied dependencies
- **Visual feedback**: Blocked tasks shown with 🚫 icon

### 🧪 Unit Tests
Comprehensive test coverage for all core modules.

- **30+ test cases**: Models, Repository, Scheduler, Dependencies
- **Pytest-based**: Industry-standard testing framework
- **Cross-platform**: Test runners for Unix and Windows
- **Easy to run**: `./run-tests.sh` or `.\run-tests.ps1`

### ⚡ Performance Index
Fast lookups for large task queues (100+ tasks).

- **O(1) lookups**: By status, agent, or priority
- **Automatic maintenance**: Index updated on task changes
- **Consistency verification**: Detect and fix index drift
- **Rebuild capability**: Reconstruct index from scratch

### 📝 Complete Documentation
All features fully documented with examples.

- **Updated AGENTS.md**: Complete feature documentation
- **Quick Start Guide**: `QUICK_START_NEW_FEATURES.md`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **Changelog**: `CHANGELOG_v3.0.md`

## Overview

The Agent Orchestrator Framework is a task queue management system for AI agents. It provides a simple, file-based approach to delegating work to specialized agents, tracking their progress, and managing asynchronous task execution. All state is persisted as files in the `.orchestra/` directory.

**Version 3.0** adds enterprise-grade features while maintaining the pure Python stdlib architecture with zero external dependencies.

## Architecture

### V3.0 Pure Python Architecture

The v3.0 system uses a **clean 2-layer architecture**:

1. **Python CLI** (`.orchestra-cli/cli/`) - High-performance core
2. **Sub-Agents** (`.opencode/agent/`) - Specialized agents for actual work

```
User → python3 -m cli start → Python CLI → Task Created
                                  ↓
                              Task Execution
                                  ↓
                         Sub-Agent (opencode run)
```

### Directory Structure

```
.orchestra/
├── tasks/          # Task definition JSON files and sentinel files (.done, .error, .cancelled, .timeout, .exitcode)
│   └── index.json  # 🆕 Task index for fast lookups
├── plans/          # Markdown plan files for each task
├── logs/           # Execution logs for each task
├── archive/        # 🆕 Archived tasks (old completed/failed tasks)
├── config.json     # 🆕 Configuration file (archival, retention policies)
└── workspace/      # Output directory for agent-generated code

.orchestra-cli/
├── cli/            # Python CLI (v2.0-v3.0) - High-performance core
│   ├── agent.py                # CLI entry point
│   ├── core/                   # Core business logic
│   │   ├── models.py           # Task data models (Pydantic-style)
│   │   ├── repository.py       # Task persistence (CRUD operations)
│   │   ├── reconciler.py       # State reconciliation logic
│   │   ├── scheduler.py        # Task scheduling (FIFO + priority + dependencies)
│   │   ├── executor.py         # Process launching and management
│   │   ├── formatter.py        # Table/output formatting
│   │   ├── config.py           # 🆕 Configuration management
│   │   ├── archive_manager.py  # 🆕 Auto-archival logic
│   │   ├── dependency_resolver.py # 🆕 Dependency resolution & cycle detection
│   │   ├── retry_manager.py    # Centralized retry logic
│   │   └── index.py            # 🆕 Task indexing for performance
│   ├── commands/               # Command implementations
│   │   ├── status.py           # Status + reconciliation + watch mode
│   │   ├── start.py            # Task creation (with dependencies)
│   │   ├── run.py              # Single/parallel execution
│   │   ├── cancel.py           # Task cancellation
│   │   ├── retry.py            # Retry failed tasks
│   │   ├── clean.py            # Clean up old tasks
│   │   ├── timeout_cmd.py      # Timeout management
│   │   ├── daemon.py           # Daemon mode (with auto-archival)
│   │   ├── archive.py          # 🆕 Archive commands
│   │   ├── config_cmd.py       # 🆕 Configuration commands
│   │   ├── deps.py             # 🆕 Dependency management
│   │   └── index_cmd.py        # 🆕 Index management
│   ├── tests/                  # 🆕 Unit tests
│   │   ├── conftest.py         # Pytest fixtures
│   │   ├── test_models.py      # Model tests
│   │   ├── test_repository.py  # Repository tests
│   │   ├── test_scheduler.py   # Scheduler tests
│   │   └── test_dependencies.py # Dependency tests
│   └── utils/                  # Utility modules
│       ├── logger.py           # Centralized logging with debug toggle
│       ├── process.py          # Cross-platform process management
│       ├── time_utils.py       # Duration formatting
│       └── paths.py            # Path constants
│
├── prompts/        # Prompt templates for agent protocol injection
│   ├── auggie.txt              # Full protocol template for Augment CLI
│   ├── default.txt             # Minimal template for generic agents
│   └── README.md               # Template documentation
│
├── scripts/        # Helper scripts
│   ├── mock-opencode.py        # Mock agent for testing
│   └── test-prompt-template.py # Template testing utility
│
└── agent-config.json           # Agent configuration (decouples CLI tools)

.opencode/
└── agent/          # Sub-agent definitions
    └── coder.md                # Code generation sub-agent
```

### Components

#### 0. Agent Configuration (Agent Decoupling + Prompt Templates)

**File:** `.orchestra-cli/agent-config.json`

This configuration file allows you to **decouple the orchestrator from specific agent implementations**. You can now use any CLI tool (OpenCode, Augment, Cursor, etc.) without modifying any code.

**Example Configuration:**
```json
{
  "agents": {
    "coder": {
      "command": "opencode",
      "args": ["run", "{prompt}", "--agent", "coder"],
      "description": "Default OpenCode agent"
    },
    "auggie": {
      "command": "auggie",
      "args": ["-i", "{prompt}", "-w", ".", "--model", "sonnet4.5", "-p"],
      "description": "Augment CLI agent (Sonnet 4.5)",
      "promptTemplateFile": ".orchestra-cli/prompts/auggie.txt"
    },
    "cursor": {
      "command": "cursor",
      "args": ["--task", "{prompt}"],
      "description": "Cursor AI agent",
      "promptTemplateFile": ".orchestra-cli/prompts/default.txt"
    }
  }
}
```

**Variable Substitution:**
- `{prompt}` - Full task prompt with completion instructions (or template content)
- `{taskId}` - Unique task identifier
- `{agent}` - Agent name

**Prompt Template Variables (when using `promptTemplateFile`):**
- `{taskId}` - Unique task identifier
- `{userPrompt}` - User's original task description
- `{planFile}` - Path to plan file
- `{logFile}` - Path to log file
- `{agent}` - Agent name

**Backward Compatibility:**
If an agent is not found in the config, the Executor falls back to the default: `opencode run {prompt} --agent {agent}`

**Usage:**
```bash
# Use Augment with full protocol injection
python3 -m cli start auggie "Refactor this function"
python3 -m cli run

# Debug mode to see the full command
python3 -m cli --debug run
```

### Components

#### 1. Python CLI
The **Python CLI** is a high-performance command-line interface that handles all orchestration logic:
- **Pure Python stdlib** (no external dependencies)
- **<100ms response time** for most commands
- **Cross-platform** (Linux/macOS/Windows)
- **Rich output** (ANSI colors, tables, status icons)
- **Watch mode** for status monitoring

**Core Modules:**
- `core/models.py`: Task data models with validation
- `core/repository.py`: Atomic JSON persistence with sentinel file management
- `core/reconciler.py`: Task state reconciliation (checks PIDs, sentinel files)
- `core/scheduler.py`: FIFO task scheduling with priority support
- `core/executor.py`: Cross-platform process launching with timeout handling (pure Python)
- `core/formatter.py`: Pretty-printed tables with ANSI colors

#### 2. Sub-Agents
Sub-agents are specialized agents defined in `.opencode/agent/` that perform actual work. They run in isolated sessions via the `opencode run` command.

**Available Sub-Agents:**
- **`coder`** (`.opencode/agent/coder.md`): Writes and modifies code based on task requirements

## Workflow

### 1. Task Creation (`python3 -m cli start <agent_name> <prompt> [options]`)

**What Happens:**
1. Generates a unique task ID using timestamp: `task_<timestamp>`
2. Parses optional flags: `--max-retries N`, `--auto-retry`, `--priority N`, `--timeout N`
4. Creates a task definition file at `.orchestra/tasks/<Task_ID>.json`:
   ```json
   {
     "taskId": "task_1234567890",
     "status": "pending",
     "agent": "coder",
     "prompt": "User's task description",
     "planFile": ".orchestra/plans/task_1234567890_plan.md",
     "logFile": ".orchestra/logs/task_1234567890.log",
     "createdAt": "2025-12-01T00:00:00Z",
     "retryCount": 0,
     "maxRetries": 3,
     "autoRetry": false,
     "priority": 5,
     "timeout": 3600,
     "timeoutWarning": 60,
     "parentTaskId": null
   }
   ```
5. Creates an empty plan file at `.orchestra/plans/<Task_ID>_plan.md` with the task prompt
6. Responds: "Task <Task_ID> created for <agent_name>."

**Key Points:**
- Tasks start in `pending` status
- Each task gets a unique ID, plan file, and log file path
- Optional retry, priority, and timeout settings can be configured at creation
- Multiple tasks can be queued

### 2. Task Execution (`python3 -m cli run`)

**What Happens:**
1. Scans `.orchestra/tasks/` for the oldest `pending` task (by file timestamp)
2. Updates the task status to `running` in the JSON file and records `startedAt`
3. Launches the specified sub-agent asynchronously in a background process
4. Records the process PID in the task JSON
5. Responds: "Started task <Task_ID> (PID: <PID>)."

**Key Points:**
- Only one task is executed per `run` invocation
- Tasks run asynchronously in the background
- **Pure Python Timeout**: Timeout handled via `subprocess.wait(timeout=N)` in a monitoring thread
- **Exit Codes**: Exit codes are captured; 124 indicates a timeout
- All output is logged to the task's log file
- The task prompt includes instructions for the agent to create a `.done` sentinel file

### 3. Agent Execution (Sub-Agent Work)

**Agent File:** `.opencode/agent/coder.md`

**What Happens:**
1. The sub-agent receives the task prompt via `opencode run`
2. **Protocol Steps:**
   - Checks for `AGENTS.md` or `CONVENTIONS.md` in the project root
   - Reads and follows any project conventions
   - Updates the plan file with its technical approach
   - Writes or modifies code (in current directory or `.orchestra/workspace/`)
   - Creates a sentinel file: `.orchestra/tasks/<Task_ID>.done`
   - Reports the absolute paths of created files (to the log)

**Key Points:**
- Sub-agents run in isolated sessions
- They respect project conventions when found
- Completion is signaled via a `.done` file (not by exit status)
- The workspace can be the current directory or a dedicated workspace

### 4. Parallel Task Execution (`python3 -m cli run --parallel [max_concurrent]`)

**What Happens:**
1. Counts currently running tasks
2. Calculates available slots: `max_concurrent - running_count`
3. Finds the oldest pending tasks (up to available slots)
4. Launches each task in the background
5. Records PIDs and `startedAt` timestamps for all launched tasks
6. Responds: "Started N task(s): task_123, task_456 (PIDs: 12345, 12346)"

**Key Points:**
- Default concurrency limit: 3 tasks
- Respects system resources by limiting parallel execution
- Each task runs independently in its own process
- Use `python3 -m cli status` to monitor progress of all running tasks

### 5. Task Retry (`python3 -m cli retry <task_id>`)

**What Happens:**
1. Validates the task exists and is in `failed` state
3. Extracts original task info (agent, prompt, error)
4. Checks if retry limit has been reached
5. Creates a new task with:
   - Same agent and prompt as original
   - Incremented `retryCount`
   - Linked via `parentTaskId` to original task
   - Optional `autoRetry` flag for automatic future retries
   - Updated `retryHistory` with failure details
   - Inherited timeout settings
6. Creates a plan file documenting the retry attempt
7. Updates original task with `retriedBy` field
8. Responds: "Task task_XXX created as retry for task_YYY (attempt 2/3)"

**Key Points:**
- Only failed tasks can be retried
- Retry count is tracked and enforced (default max: 3)
- Auto-retry flag enables automatic retries on future failures
- Full audit trail maintained via retryHistory
- Original task context is preserved

### 6. Status Check and Reconciliation (`python3 -m cli status`)

**What Happens:**
1. **Reconciliation Phase:**
   - Finds all tasks with `"status": "running"`
   - Checks if a corresponding `.done` file exists → updates to `complete`
   - Checks if a corresponding `.error` file exists → updates to `failed` and captures error message
   - Checks if a corresponding `.cancelled` file exists → updates to `cancelled`
   - **Timeout Check:** Checks for `.timeout` sentinel file or exit code 124
   - Checks if PID is still alive → if process died without sentinel file, marks as `failed`
2. **Auto-Retry Phase:**
   - For each newly failed task (including timeouts) with `autoRetry: true`:
     - Checks if `retryCount < maxRetries`
      - Calculates exponential backoff delay (2^retryCount seconds)
      - If delay has elapsed, automatically creates retry task
      - Reports: "Auto-retrying task_XXX (attempt N/M)"
3. **Reporting Phase:**
   - Reads all task JSON files
   - Outputs a Markdown table with columns:
     - ID (with ↻ symbol for retry tasks)
     - Agent
     - Status (✓ complete, ✗ failed, ⏱ running, ⏸ pending, ⊗ cancelled, 🔄 auto-retry, ⏱⚠ timeout)
     - Prompt (truncated summary)
     - Time (elapsed / timeout)
      - Retry (shows "N/M" if retryCount > 0)
      - Error/Info (error message or retry countdown)
4. **Summary Statistics:**
   - Total, running, pending, completed, failed counts
   - Number of failed tasks with auto-retry enabled
   - Number of timed-out tasks

**Key Points:**
- Reconciliation happens on-demand, not automatically
- Multiple sentinel files support different completion states
- PID health checking detects crashed processes
- Auto-retry triggers automatically for eligible tasks
- Exponential backoff prevents thrashing (2s, 4s, 8s, 16s...)
- Old completed tasks remain in the system unless manually cleaned

### 7. Timeout Management (`python3 -m cli timeout <cmd> [args]`)

**What Happens:**
- `timeout <task_id>`: Immediately terminates a task as timed out
- `timeout list`: Shows all tasks with timeouts and their remaining time
- `timeout extend <task_id> <seconds>`: Adds time to a running task's timeout

**Key Points:**
- Allows manual intervention for long-running tasks
- **Extend Limitation**: Extending a running task requires cancellation and restart
- Integrates with auto-retry (manually timed out tasks can still auto-retry if enabled)

### 8. Configuration Management (`python3 -m cli config <cmd>`) - v3.0

**What Happens:**
- `config init`: Creates default configuration file at `.orchestra/config.json`
- `config show`: Displays current configuration settings
- `config set <key> <value>`: Updates a configuration value

**Configuration Options:**
- `archive.enabled`: Enable/disable auto-archival (true/false)
- `archive.max_completed_age_days`: Days before archiving completed tasks (default: 7)
- `archive.max_failed_age_days`: Days before archiving failed tasks (default: 14)
- `archive.max_queue_size`: Maximum queue size before warning (default: 100)
- `archive.archive_dir`: Directory for archived tasks (default: .orchestra/archive)

**Key Points:**
- Configuration is optional (defaults work fine)
- Changes take effect immediately
- Daemon uses config for auto-archival

### 9. Archive Management (`python3 -m cli archive [options]`) - v3.0

**What Happens:**
- `archive`: Archives old completed/failed tasks based on retention policy
- `archive --dry-run`: Preview what would be archived without doing it
- `archive --force`: Archive even if auto-archival is disabled in config
- `archive stats`: Show archive statistics (count, size, location)

**Archival Process:**
1. Identifies tasks older than retention period
2. Copies task JSON, plan, and log files to archive directory
3. Deletes original files from tasks directory
4. Updates archive statistics

**Key Points:**
- Respects retention policies from config
- Asks for confirmation if archiving >10 tasks
- Daemon runs archival automatically every hour
- Archived tasks can be restored manually if needed

### 10. Dependency Management (`python3 -m cli deps <cmd>`) - v3.0

**What Happens:**
- `deps show <task_id>`: Shows dependencies for a specific task
- `deps graph`: Displays full dependency graph for all tasks
- `deps validate`: Checks for circular dependencies

**Dependency Features:**
- Tasks can depend on one or more other tasks
- Circular dependencies are detected and prevented
- Blocked tasks shown with 🚫 icon in status
- Scheduler only runs tasks with satisfied dependencies

**Key Points:**
- Dependencies specified at task creation with `--depends-on`
- If a dependency fails, dependent tasks are blocked
- If a dependency is cancelled, dependent tasks are blocked
- Dependencies are validated before task creation

### 11. Index Management (`python3 -m cli index <cmd>`) - v3.0

**What Happens:**
- `index rebuild`: Rebuilds task index from scratch
- `index stats`: Shows index statistics (counts by status/agent/priority)
- `index verify`: Verifies index consistency with actual tasks

**Index Benefits:**
- O(1) lookups by status, agent, or priority
- Faster status command for large queues (100+ tasks)
- Reduced disk I/O for common queries
- Automatic maintenance on task changes

**Key Points:**
- Index is automatically updated on task changes
- Rebuild if index becomes inconsistent
- Verify periodically to ensure consistency
- Optional but recommended for large queues

## All Commands Reference (v3.0)

| Command | Description | Example |
|---------|-------------|---------|
| `start` | Create a new task | `python3 -m cli start coder "Build API" --depends-on task_1` |
| `run` | Execute pending tasks | `python3 -m cli run --parallel 3` |
| `daemon` | Run in daemon mode | `python3 -m cli daemon --max-concurrent 3 --interval 5` |
| `status` | View task status | `python3 -m cli status --watch` |
| `cancel` | Cancel a task | `python3 -m cli cancel task_123` |
| `retry` | Retry a failed task | `python3 -m cli retry task_123 --auto` |
| `clean` | Remove old tasks | `python3 -m cli clean completed` |
| `timeout` | Manage timeouts | `python3 -m cli timeout extend task_123 300` |
| `config` | Manage configuration | `python3 -m cli config init` |
| `archive` | Archive old tasks | `python3 -m cli archive --dry-run` |
| `deps` | Manage dependencies | `python3 -m cli deps graph` |
| `index` | Manage task index | `python3 -m cli index rebuild` |

### Start Command Options

```bash
python3 -m cli start <agent> <prompt> [options]

Options:
  --max-retries N        Maximum retry attempts (default: 3)
  --auto-retry           Enable automatic retries
  --priority N           Task priority 1-10 (default: 5, higher = more important)
  --timeout N            Timeout in seconds
  --depends-on TASK_ID [TASK_ID ...]  Task IDs this task depends on (v3.0)
```

### Config Command Options

```bash
python3 -m cli config init                    # Create default config
python3 -m cli config show                    # Show current config
python3 -m cli config set <key> <value>       # Set config value

Available keys:
  archive.enabled                    # true/false
  archive.max_completed_age_days     # integer (days)
  archive.max_failed_age_days        # integer (days)
  archive.max_queue_size             # integer (max tasks)
  archive.archive_dir                # string (path)
```

### Archive Command Options

```bash
python3 -m cli archive                # Archive old tasks
python3 -m cli archive --dry-run      # Preview without archiving
python3 -m cli archive --force        # Archive even if disabled
python3 -m cli archive stats          # Show archive statistics
```

### Deps Command Options

```bash
python3 -m cli deps show <task_id>    # Show task dependencies
python3 -m cli deps graph             # Show full dependency graph
python3 -m cli deps validate          # Check for circular dependencies
```

### Index Command Options

```bash
python3 -m cli index rebuild          # Rebuild index from scratch
python3 -m cli index stats            # Show index statistics
python3 -m cli index verify           # Verify index consistency
```

## Task States

Tasks can be in one of five states:

1. **`pending`**: Task created but not yet started
2. **`running`**: Task is being executed by a sub-agent (process is active)
3. **`complete`**: Task finished successfully (reconciled via `.done` file)
4. **`failed`**: Task failed (process died, error occurred, timeout, or explicit failure via `.error` file)
5. **`cancelled`**: Task was cancelled by user via `python3 -m cli cancel`

**Additional States (v3.0):**
- **`blocked`**: Task is pending but blocked by unsatisfied dependencies (shown with 🚫 icon)

## Error Handling and Task Management

### Enhanced Status Reconciliation

The `status` command performs comprehensive health checks:

- **Process Health**: Checks if PIDs for running tasks are still alive using `ps -p $PID`
- **Error Detection**: Detects `.error` sentinel files created by failing agents
- **Cancellation Detection**: Recognizes `.cancelled` files from cancelled tasks
- **Timeout Detection**: Checks elapsed time against timeout limits
- **Automatic Failover**: Updates tasks to `failed` state when process dies unexpectedly

### Task Cancellation (`python3 -m cli cancel <task_id>`)

Cancel running or pending tasks gracefully:

- **Pending Tasks**: Immediately cancelled, status updated to `cancelled`
- **Running Tasks**: Process terminated with SIGTERM, then SIGKILL if needed
- **Completed/Failed Tasks**: Cannot be cancelled (reports current status)

**Usage:**
```bash
python3 -m cli cancel task_1234567890
```

**What Happens:**
1. Validates task exists
2. Reads current status and PID
3. If running: sends SIGTERM, waits 3 seconds, sends SIGKILL if still alive
4. Updates status to `cancelled`
5. Creates `.cancelled` sentinel file
6. Reports: "Task <ID> cancelled (PID: <PID> terminated)."

### Error Sentinel Files

Sub-agents now create `.error` files when failures occur:

**Location**: `.orchestra/tasks/<Task_ID>.error`

**Format**: JSON with error details
```json
{
  "error": "Brief error description",
  "details": "Full error message or stack trace",
  "timestamp": "2025-12-01T10:30:00Z"
}
```

The status command reads these files, updates the task JSON with the error message, and deletes the `.error` file during reconciliation.

### Task Cleanup (`python3 -m cli clean [filter]`)

Remove old task files to keep the workspace clean:

**Filters:**
- `completed` (default) - Remove completed tasks
- `failed` - Remove failed tasks
- `cancelled` - Remove cancelled tasks
- `all` - Remove all non-running/non-pending tasks
- `task_XXXXX` - Remove specific task by ID

**Usage:**
```bash
python3 -m cli clean completed    # Remove completed tasks
python3 -m cli clean failed       # Remove failed tasks
python3 -m cli clean all          # Remove all finished tasks
python3 -m cli clean task_123     # Remove specific task
```

**Safety:** 
- Never deletes `running` or `pending` tasks
- Asks for confirmation if more than 10 tasks match
- Removes JSON, plan, log, and sentinel files

### Enhanced Task JSON Schema

Tasks now include retry tracking, priority, timeout, dependencies, and error tracking fields:

```json
{
  "taskId": "task_1234567890",
  "status": "failed",
  "agent": "coder",
  "prompt": "Create a web server",
  "planFile": ".orchestra/plans/task_1234567890_plan.md",
  "logFile": ".orchestra/logs/task_1234567890.log",
  "createdAt": "2025-12-01T10:00:00Z",
  "pid": "12345",
  "errorMessage": "Task timed out after 3600 seconds",
  "retryCount": 1,
  "maxRetries": 3,
  "autoRetry": true,
  "priority": 5,
  "timeout": 3600,
  "startedAt": "2025-12-01T10:00:00Z",
  "timedOutAt": "2025-12-01T11:00:00Z",
  "parentTaskId": "task_1234567000",
  "retriedBy": "task_1234567999",
  "retriedAt": "2025-12-01T11:05:00Z",
  "retryHistory": [
    {
      "attempt": 1,
      "timestamp": "2025-12-01T10:00:00Z",
      "error": "Network timeout",
      "retriedFrom": "task_1234567000"
    }
  ],
  "dependsOn": ["task_1234567888", "task_1234567889"],
  "blockedBy": "task_1234567888",
  "blockedReason": "Dependency task_1234567888 failed"
}
```

**New Fields (v3.0):**
- `dependsOn`: Array of task IDs this task depends on
- `blockedBy`: Task ID currently blocking this task (if any)
- `blockedReason`: Human-readable reason why task is blocked

## Implementation Details

### How Sub-Agents Work
- Sub-agents are markdown files in `.opencode/agent/`
- The `mode: subagent` field marks them as sub-agents
- The `tools` field specifies which OpenCode tools they can access
- They run in separate `opencode run` sessions, isolated from the main orchestrator

### Completion Signaling
- The `.done` file approach allows asynchronous completion detection
- Sub-agents control when they're "done" (not the orchestrator)
- This decouples agent execution time from orchestrator responsiveness

### Process Management
- Tasks run as background processes (via `&`)
- PIDs are stored but not actively monitored
- No automatic cleanup or timeout handling (manual intervention required if stuck)

## Performance Benchmarks

The v2.0 Python CLI provides significant performance improvements over the LLM-based implementation:

| Command | LLM (v1.0) | Python CLI (v2.0) | Speedup | Notes |
|---------|------------|-------------------|---------|-------|
| `status` | 2-5s | <100ms | **20-50x** | Includes reconciliation and formatting |
| `start` | 1-2s | <50ms | **20-40x** | Task creation with validation |
| `run` | 1-3s | <200ms | **5-15x** | Single task launch |
| `run --parallel` | 2-4s | <300ms | **7-13x** | Multiple task launch |
| `cancel` | 1-2s | <100ms | **10-20x** | Process termination |
| `retry` | 2-3s | <150ms | **13-20x** | Retry task creation |
| `clean` | 2-4s | <200ms | **10-20x** | File deletion |
| `timeout` | 2-3s | <100ms | **20-30x** | Timeout management |

**Key Factors:**
- **No LLM latency**: Python executes directly without waiting for model inference
- **Atomic operations**: File I/O is optimized with atomic writes
- **Pure stdlib**: No package loading overhead (no pip dependencies)
- **Minimal parsing**: JSON parsing is native and fast

**Watch Mode Performance:**
- Status updates every 2-5 seconds with minimal CPU usage (<1%)
- Real-time reconciliation with no noticeable delay
- Can monitor dozens of tasks simultaneously

## Setup Guide

### Using the Python CLI

**Setup (add to .bashrc or run once per session):**
```bash
export PYTHONPATH=.orchestra-cli:$PYTHONPATH

# Use Python CLI
python3 -m cli start coder "Create a web server"
python3 -m cli run
python3 -m cli status --watch
```

**Alias for Convenience:**
```bash
# Add to .bashrc or .zshrc
alias agent='cd /path/to/agent-orchestrator && PYTHONPATH=.orchestra-cli:$PYTHONPATH python3 -m cli'

# Usage
agent status
agent start coder "Build a feature"
agent run --parallel 3
```

## Usage Examples

### Example 1: Simple Task

```bash
python3 -m cli start coder "Write a Hello World function in Python"
python3 -m cli run
# ... wait for completion ...
python3 -m cli status
```

### Example 2: Multiple Tasks
```bash
python3 -m cli start coder "Create a REST API server"
python3 -m cli start coder "Write unit tests for the API"
python3 -m cli status    # Shows 2 pending tasks
python3 -m cli run       # Starts first task
python3 -m cli run       # Starts second task
python3 -m cli status    # Shows progress
```

### Example 3: Cancel and Retry
```bash
python3 -m cli start coder "Generate a large dataset"
python3 -m cli run
# Oops, wrong parameters!
python3 -m cli status    # Get the task ID
python3 -m cli cancel task_1234567890
python3 -m cli start coder "Generate a large dataset with correct parameters"
python3 -m cli run
```

### Example 4: Cleanup
```bash
python3 -m cli status    # Check completed tasks
python3 -m cli clean completed    # Remove all completed tasks
python3 -m cli clean failed       # Remove failed tasks
python3 -m cli clean all          # Remove all finished tasks
```

### Example 5: Parallel Execution
```bash
# Queue multiple tasks
python3 -m cli start coder Create user authentication module
python3 -m cli start coder Write API documentation
python3 -m cli start coder Implement logging system
python3 -m cli start coder Add unit tests
python3 -m cli start coder Create integration tests

# Check queue status
python3 -m cli status
# | ID         | Agent | Status | Prompt                    |
# | task_12345 | coder | ⏸      | Create user auth...       |
# | task_12346 | coder | ⏸      | Write API docs...         |
# | task_12347 | coder | ⏸      | Implement logging...      |
# | task_12348 | coder | ⏸      | Add unit tests...         |
# | task_12349 | coder | ⏸      | Create integration...     |

# Launch 3 tasks in parallel (default concurrency)
python3 -m cli run --parallel
# Started 3 task(s): task_12345, task_12346, task_12347 (PIDs: 98765, 98766, 98767)
# Running: 3/3 tasks

# Check status - 3 running concurrently
python3 -m cli status
# | ID         | Agent | Status | Prompt                    |
# | task_12345 | coder | ⏱      | Create user auth...       |
# | task_12346 | coder | ⏱      | Write API docs...         |
# | task_12347 | coder | ⏱      | Implement logging...      |
# | task_12348 | coder | ⏸      | Add unit tests...         |
# | task_12349 | coder | ⏸      | Create integration...     |

# After some tasks complete, launch remaining
python3 -m cli run --parallel
# Started 2 task(s): task_12348, task_12349 (PIDs: 98768, 98769)
# Running: 3/3 tasks

# Launch with higher concurrency
python3 -m cli run --parallel 5
# Started 5 task(s): ... (PIDs: ...)
```

### Example 6: Manual Retry
```bash
# Task fails
python3 -m cli status
# | ID         | Agent | Status | Prompt                | Error              |
# | task_12345 | coder | ✗      | Deploy to prod...     | Network timeout    |

# Retry the failed task
python3 -m cli retry task_12345
# Task task_12346 created as retry for task_12345 (attempt 1/3)
# Use python3 -m cli run to execute the retry

# Run the retry
python3 -m cli run
# Started task task_12346 (PID: 98770)

# Check status - shows retry link
python3 -m cli status
# | ID         | Agent | Status | Prompt                | Retry |
# | task_12345 | coder | ✗      | Deploy to prod...     |       |
# | ↻ task_12346 | coder | ⏱      | Deploy to prod...     | 1/3   |
```

### Example 7: Auto-Retry
```bash
# Create task with auto-retry enabled
python3 -m cli start coder "Deploy microservice to production" --max-retries 5 --auto-retry
# Task task_12345 created for coder.
# Max retries: 5
# Auto-retry: enabled

# Run the task
python3 -m cli run
# Started task task_12345 (PID: 98765)

# Task fails, check status
python3 -m cli status
# Auto-retrying task_12345 (attempt 2/5)
# | ID           | Agent | Status | Prompt                | Retry | Error/Info        |
# | task_12345   | coder | ✗      | Deploy microser...    | 1/5   | Connection failed |
# | ↻ task_12346 | coder | ⏸      | Deploy microser...    | 2/5   | auto-retry        |

# Wait for backoff delay (2^1 = 2 seconds), then status again
python3 -m cli status
# Task task_12346 automatically queued for execution

# Run it
python3 -m cli run
# Started task task_12346 (PID: 98766)

# Fails again - longer backoff
python3 -m cli status
# | ID           | Agent | Status | Prompt                | Retry | Error/Info        |
# | task_12345   | coder | ✗      | Deploy microser...    | 1/5   | Connection failed |
# | task_12346   | coder | ✗      | Deploy microser...    | 2/5   | Connection failed |
# | ↻ task_12347 | coder | 🔄     | Deploy microser...    | 3/5   | retry in 4s       |

# After 4 seconds, auto-retry triggers
python3 -m cli status
# | ↻ task_12347 | coder | ⏸      | Deploy microser...    | 3/5   | auto-retry        |

# Eventually succeeds
python3 -m cli run
python3 -m cli status
# | ID           | Agent | Status | Prompt                | Retry |
# | ↻ task_12347 | coder | ✓      | Deploy microser...    | 3/5   |
```

### Example 8: Combining Parallel Execution and Auto-Retry
```bash
# Queue multiple tasks with auto-retry
python3 -m cli start coder "Task 1" --auto-retry
python3 -m cli start coder "Task 2" --auto-retry
python3 -m cli start coder "Task 3" --auto-retry
python3 -m cli start coder "Task 4" --auto-retry

# Launch all in parallel
python3 -m cli run --parallel 4
# Started 4 task(s): task_12345, task_12346, task_12347, task_12348

# Some tasks fail, auto-retry kicks in
python3 -m cli status
# Auto-retrying task_12345 (attempt 2/3)
# Auto-retrying task_12347 (attempt 2/3)
# | ID           | Agent | Status | Prompt     | Retry | Error/Info        |
# | task_12345   | coder | ✗      | Task 1     | 1/3   | Error X           |
# | task_12346   | coder | ✓      | Task 2     |       |                   |
# | task_12347   | coder | ✗      | Task 3     | 1/3   | Error Y           |
# | task_12348   | coder | ⏱      | Task 4     |       |                   |
# | ↻ task_12349 | coder | ⏸      | Task 1     | 2/3   | auto-retry        |
# | ↻ task_12350 | coder | ⏸      | Task 3     | 2/3   | auto-retry        |

# Run retries in parallel
python3 -m cli run --parallel
# Started 2 task(s): task_12349, task_12350
```

### Example 9: Task Timeout Management
```bash
# Start a task with a timeout (e.g., 5 minutes = 300s)
python3 -m cli start coder "Run infinite loop" --timeout 300
# Task task_12345 created... Timeout: 300s (5m)

python3 -m cli run
# Started task task_12345...

# Check status - shows elapsed time and limit
python3 -m cli status
# | ID         | Agent | Status | Prompt             | Time        |
# | task_12345 | coder | ⏱      | Run infinite...    | 2m / 5m     |

# Extend timeout if needed
python3 -m cli timeout extend task_12345 300
# Extended timeout for task task_12345 by 300s (new limit: 600s, 10m)

# Force timeout immediately
python3 -m cli timeout task_12345
# Task task_12345 timed out (PID: 12345 terminated)

# Status reflects timeout
python3 -m cli status
# | ID         | Agent | Status | Prompt             | Time        | Error              |
# | task_12345 | coder | ✗      | Run infinite...    | ⏱ timeout   | Manually timed out |
```

### Example 10: Daemon Mode (Background Execution)
```bash
# Run orchestrator as a daemon that continuously executes tasks
python3 -m cli daemon --max-concurrent 3 --interval 5

# Output:
# ============================================================
# Agent Orchestrator Daemon Started
# Max concurrent tasks: 3
# Check interval: 5s
# Press Ctrl+C to stop
# ============================================================
# Status: 2 running, 3 pending, 5 completed, 0 failed
# Launched task task_12345 (PID: 98765, agent: coder)
# Launched task task_12346 (PID: 98766, agent: coder)
# Status: 3 running, 1 pending, 5 completed, 0 failed
# ...

# The daemon automatically:
# - Reconciles running tasks (checks for completion/failure)
# - Auto-retries failed tasks with exponential backoff
# - Launches pending tasks up to concurrency limit
# - Monitors task health and updates status

# Queue multiple tasks and let daemon handle them
python3 -m cli start coder "Task 1" --auto-retry
python3 -m cli start coder "Task 2" --auto-retry
python3 -m cli start coder "Task 3" --auto-retry

# In another terminal, start daemon
python3 -m cli daemon --max-concurrent 2 --interval 3

# Daemon will automatically execute all tasks with concurrency control
```

**Key Features:**
- **Automatic reconciliation**: Continuously checks task status
- **Auto-retry**: Automatically retries failed tasks with backoff
- **Concurrency control**: Limits parallel execution
- **Graceful shutdown**: Handles Ctrl+C and SIGTERM signals
- **Real-time monitoring**: Shows status updates every interval
- **Auto-archival**: Automatically archives old tasks every hour (v3.0)

### Example 11: Auto-Archival and Configuration
```bash
# Initialize configuration
python3 -m cli config init
# Created default configuration at .orchestra/config.json

# View current configuration
python3 -m cli config show
# Current Configuration:
#   archive.enabled: False
#   archive.max_completed_age_days: 7
#   archive.max_failed_age_days: 14
#   archive.max_queue_size: 100
#   archive.archive_dir: .orchestra/archive

# Enable auto-archival
python3 -m cli config set archive.enabled true
python3 -m cli config set archive.max_completed_age_days 7
python3 -m cli config set archive.max_failed_age_days 14

# Preview what would be archived
python3 -m cli archive --dry-run
# Found 5 task(s) eligible for archival:
#   task_12345 (complete, 10 days old)
#   task_12346 (complete, 8 days old)
#   task_12347 (failed, 15 days old)
#   ...

# Archive old tasks
python3 -m cli archive
# Archived: 5, Errors: 0
# Archive contains 5 tasks (0.12 MB)

# View archive statistics
python3 -m cli archive stats
# Archive Statistics:
#   Total archived tasks: 5
#   Total size: 0.12 MB
#   Location: .orchestra/archive
#
# Auto-archival: ENABLED
#   Completed tasks: archived after 7 days
#   Failed tasks: archived after 14 days
#   Queue size limit: 100 tasks

# Daemon automatically archives every hour
python3 -m cli daemon --max-concurrent 3
# ... (daemon runs with auto-archival)
```

### Example 12: Task Dependencies and DAG Execution
```bash
# Create a deployment pipeline with dependencies
python3 -m cli start coder "Setup infrastructure" --priority 10
# Task task_1733123456789 created for coder

python3 -m cli start coder "Deploy backend API" --depends-on task_1733123456789 --priority 9
# Task task_1733123456790 created for coder
#   Dependencies: task_1733123456789

python3 -m cli start coder "Deploy frontend" --depends-on task_1733123456789 --priority 9
# Task task_1733123456791 created for coder
#   Dependencies: task_1733123456789

python3 -m cli start coder "Run integration tests" --depends-on task_1733123456790 task_1733123456791 --priority 8
# Task task_1733123456792 created for coder
#   Dependencies: task_1733123456790, task_1733123456791

# View dependency graph
python3 -m cli deps graph
# Dependency Graph:
#
# task_1733123456790 (pending)
#   └─> task_1733123456789 (pending)
# task_1733123456791 (pending)
#   └─> task_1733123456789 (pending)
# task_1733123456792 (pending)
#   └─> task_1733123456790 (pending)
#   └─> task_1733123456791 (pending)

# Validate for circular dependencies
python3 -m cli deps validate
# ✓ No circular dependencies found

# View dependencies for a specific task
python3 -m cli deps show task_1733123456792
# Task: task_1733123456792
# Status: pending
#
# Dependencies (2):
#   ⏸ task_1733123456790 (pending)
#   ⏸ task_1733123456791 (pending)

# Run tasks - they execute in dependency order
python3 -m cli run --parallel 3
# Started task task_1733123456789 (PID: 12345)
# (task_1733123456790 and task_1733123456791 are blocked until task_1733123456789 completes)

# Check status - blocked tasks shown with 🚫 icon
python3 -m cli status
# | ID                  | Agent | Status    | Prompt                | Info           |
# | task_1733123456789  | coder | ⏱ running | Setup infrastructure  | -              |
# | task_1733123456790  | coder | ⏸ pending | Deploy backend API    | deps: 1        |
# | task_1733123456791  | coder | ⏸ pending | Deploy frontend       | deps: 1        |
# | task_1733123456792  | coder | ⏸ pending | Run integration tests | deps: 2        |

# After task_1733123456789 completes, dependent tasks become ready
# Next run will execute task_1733123456790 and task_1733123456791 in parallel
```

### Example 13: Performance Index
```bash
# Rebuild index for better performance (useful for large queues)
python3 -m cli index rebuild
# Rebuilding task index...
# ✓ Index rebuilt with 42 tasks

# View index statistics
python3 -m cli index stats
# Task Index Statistics:
#   Total tasks: 42
#   Last updated: 2025-12-02T10:30:00
#
# By Status:
#   complete: 25
#   failed: 5
#   pending: 10
#   running: 2
#
# By Agent:
#   coder: 35
#   auggie: 7
#
# By Priority:
#   Priority 10: 5
#   Priority 5: 30
#   Priority 1: 7

# Verify index consistency
python3 -m cli index verify
# Verifying index consistency...
# ✓ Index is consistent

# If index is out of sync
python3 -m cli index verify
# ⚠ 3 tasks missing from index:
#   - task_12345
#   - task_12346
#   - task_12347
# Run 'python3 -m cli index rebuild' to fix inconsistencies
```

### Example 14: Running Tests
```bash
# Run all tests (Unix/Linux/macOS)
cd .orchestra-cli
chmod +x run-tests.sh
./run-tests.sh
# Running Agent Orchestrator Tests
# =================================
#
# ============================= test session starts ==============================
# collected 30 items
#
# cli/tests/test_models.py ........                                       [ 26%]
# cli/tests/test_repository.py .......                                    [ 50%]
# cli/tests/test_scheduler.py .......                                     [ 73%]
# cli/tests/test_dependencies.py ........                                 [100%]
#
# ============================== 30 passed in 2.45s ==============================
# =================================
# Tests completed!

# Run tests on Windows
cd .orchestra-cli
.\run-tests.ps1

# Run specific test file
cd .orchestra-cli
pytest cli/tests/test_dependencies.py -v

# Run with coverage (if pytest-cov installed)
pytest cli/tests/ --cov=cli.core --cov-report=html
```

## Extending the Framework

### Adding a New Sub-Agent
1. Create a new file in `.opencode/agent/<agent_name>.md`
2. Define the agent's role, tools, and protocol
3. Ensure it creates a `.done` file upon completion
4. Use it via `python3 -m cli start <agent_name> <prompt>`

**Example Linux/macOS Usage:**
```bash
# Unix shell
export PYTHONPATH=.orchestra-cli:$PYTHONPATH
python3 -m cli status --watch
python3 -m cli start coder "Create a web server"
python3 -m cli run
```

### Switchable Debug Logging (v2.2)

Debug logging can be enabled or disabled via CLI flag or environment variable:

**CLI Flag:**
```bash
# Enable debug logging for a single command
python3 -m cli --debug run
python3 -m cli --debug status --watch
python3 -m cli -d start coder "Task"  # Short form
```

**Environment Variable:**
```bash
# Enable debug logging for all commands
export AGENT_DEBUG=1
python3 -m cli run

# Windows PowerShell
$env:AGENT_DEBUG = "1"
python -m cli run
```

**Log Levels:**
- `DEBUG:` - Detailed information (command building, escaping, process details) - **only shown when debug enabled**
- `INFO:` - Task lifecycle events (launch, completion) - always shown
- `WARNING:` - Recoverable errors or unexpected conditions - always shown
- `ERROR:` - Critical failures requiring attention - always shown

**Color Coding (TTY only):**
- DEBUG: Gray
- INFO: Green
- WARNING: Yellow
- ERROR: Red

**Example Debug Output:**
```
INFO: Loaded 2 agent configurations from .opencode/agent-config.json
DEBUG: Building command for agent 'auggie' using config
DEBUG: Loaded prompt template from .opencode/prompts/auggie.txt
DEBUG: Escaped newlines for Windows shell (prompt length: 2464 chars)
DEBUG: Launching task task_123
DEBUG: Agent: auggie
DEBUG: Command array length: 8 elements
DEBUG: Full command: ['auggie', '-i', '...', '-w', '.', '--model', 'sonnet4.5', '-p']
DEBUG: Executable: auggie
DEBUG: Arguments (7):
DEBUG:   [1] -i
DEBUG:   [2] You are a specialized coding agent... (2464 chars)
DEBUG:   [3] -w
DEBUG:   [4] .
DEBUG:   [5] --model
DEBUG:   [6] sonnet4.5
DEBUG:   [7] -p
DEBUG: Using Windows process creation (creationflags=512, shell=True)
DEBUG: Shell command string: auggie -i "You are a specialized..."
INFO: Task task_123 launched successfully (PID: 12345)
DEBUG: Waiting for task task_123 (timeout: 120s)
```

**Logger Utility:**

The logging system is implemented in `.orchestra-cli/cli/utils/logger.py`:

```python
from cli.utils.logger import logger

logger.debug("Only shows when debug enabled")  # Controlled by --debug or AGENT_DEBUG
logger.info("Always shows")                     # Task lifecycle events
logger.warning("Always shows")                  # Recoverable errors
logger.error("Always shows")                    # Critical failures

# Programmatic control
from cli.utils.logger import set_debug
set_debug(True)   # Enable debug logging
set_debug(False)  # Disable debug logging
```

## Prompt Templates (v2.2)

Prompt templates allow you to inject the full orchestration protocol into agents that don't support the `.opencode/agent/` subagent system (like Augment, Cursor, etc.).

### Why Prompt Templates?

- **Agent Protocol Injection**: Agents like Augment don't have a built-in subagent configuration system
- **Full Instructions**: Templates inject comprehensive instructions directly into the prompt
- **Framework Compliance**: Ensures agents follow the framework protocol (task IDs, sentinel files, error handling)

### Creating a Prompt Template

1. **Create a template file** in `.orchestra-cli/prompts/`:

```text
You are a coding agent.

Task ID: {taskId}
Task: {userPrompt}
Plan File: {planFile}
Log File: {logFile}

PROTOCOL:
1. Complete the task as requested
2. Create .orchestra/tasks/{taskId}.done when finished successfully
3. On failure, create .orchestra/tasks/{taskId}.error with JSON error details:
   {{
     "error": "Brief description",
     "details": "Full error message",
     "timestamp": "ISO 8601 timestamp"
   }}

CRITICAL: You MUST create either .done or .error file, or the orchestrator cannot detect completion!
```

2. **Reference it in `agent-config.json`:**

```json
{
  "agents": {
    "myagent": {
      "command": "myagent",
      "args": ["--prompt", "{prompt}"],
      "promptTemplateFile": ".orchestra-cli/prompts/myagent.txt"
    }
  }
}
```

### Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{taskId}` | Unique task identifier | `task_1764601210546` |
| `{userPrompt}` | User's original task description | `Create a REST API` |
| `{planFile}` | Path to plan file | `.orchestra/plans/task_XXX_plan.md` |
| `{logFile}` | Path to log file | `.orchestra/logs/task_XXX.log` |
| `{agent}` | Agent name | `auggie`, `coder`, etc. |

### Included Templates

- **`auggie.txt`**: Full protocol for Augment CLI (60+ lines)
  - Convention checking (PROJECT.md, CONVENTIONS.md)
  - Plan file updates
  - Workspace management
  - Comprehensive error handling

- **`default.txt`**: Minimal template for generic agents (24 lines)
  - Basic task execution
  - Simple completion signaling

### Platform-Specific Escaping

On Windows, newlines in the prompt template would break shell argument parsing. The executor automatically escapes newlines for Windows:

```python
# Windows (shell=True): Newlines are escaped
prompt = prompt.replace('\n', '\\n')

# Linux/macOS (shell=False): Newlines are preserved as-is
# No escaping needed - passed directly to execve()
```

This ensures the full multi-line template is passed correctly to the agent on all platforms.

### Testing Templates

Use the `--debug` flag to verify templates are working:

```bash
python3 -m cli --debug start auggie "Test task"
python3 -m cli --debug run

# Output shows:
# DEBUG: Loaded prompt template from .orchestra-cli/prompts/auggie.txt
# DEBUG: Escaped newlines for Windows shell (prompt length: 2464 chars)
# DEBUG:   [2] You are a specialized coding agent... (2464 chars)
```

## Limitations and Considerations

### ✅ Resolved in v2.0-v2.2

**Phase 1 - Foundation:**
- ✅ **Task cancellation**: Available via `python3 -m cli cancel` or `python3 -m cli cancel`
- ✅ **Failure handling**: Failed tasks detected via PID health checks and `.error` files
- ✅ **Task cleanup**: Available via `python3 -m cli clean` or `python3 -m cli clean`
- ✅ **Performance**: 20-50x improvement with Python CLI
- ✅ **Parallel execution**: Available via `python3 -m cli run --parallel N`
- ✅ **Retry mechanism**: Available via `python3 -m cli retry` with auto-retry support
- ✅ **Timeout handling**: Available via `python3 -m cli timeout` commands
- ✅ **Watch mode**: Real-time status monitoring with `--watch` flag

**Cross-Platform (v2.1):**
- ✅ **Windows support**: Native Windows process management (no WSL required)
- ✅ **Agent decoupling**: Configuration-driven agent execution
- ✅ **Pure Python timeout**: No shell script dependencies
- ✅ **Defensive logging**: Debug output for troubleshooting cross-platform issues

**Agent Integration (v2.2):**
- ✅ **Prompt Templates**: Inject orchestration protocol into any agent (Augment, Cursor, etc.)
- ✅ **Switchable Debug Logging**: `--debug` flag and `AGENT_DEBUG` environment variable
- ✅ **Platform-Specific Escaping**: Automatic newline escaping for Windows shell compatibility
- ✅ **Centralized Logger**: Color-coded logging utility with debug toggle
- ✅ **Augment Support**: Full integration with Augment CLI via prompt template

### ⏳ Current Limitations

**Known Issues:**
- ~~**Auto-retry integration**~~: ✅ **RESOLVED** - Implemented in `status.py` and `daemon.py`
- ~~**Task prioritization**~~: ✅ **RESOLVED** - Priority sorting implemented in `scheduler.py` (line 32)
- **Automatic cleanup**: No background auto-archival (manual `python3 -m cli clean` required)
- ~~**Manual reconciliation**~~: ✅ **RESOLVED** - Daemon mode available via `python3 -m cli daemon`

**Design Trade-offs:**
- **No dependencies**: Chose pure stdlib over feature-rich libraries (Click, Rich, Pydantic runtime)
- **File-based state**: Simple but not suitable for very large task queues (100s of tasks)
- **GNU timeout limitation**: Cannot dynamically extend timeout for running processes
- **LSP errors**: Import errors shown in IDE but runtime works via PYTHONPATH trick

**Completed Enhancements (v3.0):**
- ✅ ~~Implement auto-retry logic in status reconciliation~~ - **DONE** (v2.2)
- ✅ ~~Add priority-based task scheduling~~ - **DONE** (v2.2)
- ✅ ~~Create background daemon for automatic reconciliation~~ - **DONE** (v2.2)
- ✅ ~~Add task queue size limits and archiving~~ - **DONE** (v3.0)
- ✅ ~~Implement retry with exponential backoff delays~~ - **DONE** (v2.2)
- ✅ ~~Add task dependencies and DAG execution~~ - **DONE** (v3.0)
- ✅ ~~Add comprehensive unit tests~~ - **DONE** (v3.0)
- ✅ ~~Add performance indexing~~ - **DONE** (v3.0)

**Future Enhancements:**
- [ ] Web UI dashboard for task monitoring
- [ ] Metrics and observability (Prometheus/Grafana)
- [ ] Notification system (Slack/email alerts)
- [ ] Task templates and reusable configurations
- [ ] Distributed execution across multiple nodes
- [ ] Scheduled tasks (cron-like scheduling)
