# OpenCode Agent Orchestrator Framework

This document describes the file-system-based agent orchestration framework built on top of OpenCode's custom command and agent system.

## Overview

The Agent Orchestrator Framework is a task queue management system for AI agents. It provides a simple, file-based approach to delegating work to specialized agents, tracking their progress, and managing asynchronous task execution. All state is persisted as files in the `.gemini/agents/` directory.

## Architecture

### Directory Structure

```
.gemini/agents/
├── tasks/          # Task definition JSON files and sentinel files (.done, .error, .cancelled)
├── plans/          # Markdown plan files for each task
├── logs/           # Execution logs for each task
└── workspace/      # Output directory for agent-generated code

.opencode/
├── command/        # Custom slash command definitions
│   ├── agent-start.md
│   ├── agent-run.md
│   ├── agent-run-parallel.md  # NEW (Phase 2): Parallel execution
│   ├── agent-status.md
│   ├── agent-retry.md         # NEW (Phase 2): Retry failed tasks
│   ├── agent-cancel.md
│   └── agent-clean.md
└── agent/          # Sub-agent definitions
    └── coder.md
```

### Components

#### 1. Orchestrator (Main Agent)
The **Orchestrator** is implemented as a series of custom OpenCode commands. It manages the task lifecycle but does not execute tasks itself. Instead, it:
- Creates and tracks tasks
- Queues tasks for execution
- Delegates work to specialized sub-agents
- Reconciles completed tasks

#### 2. Sub-Agents
Sub-agents are specialized agents defined in `.opencode/agent/` that perform actual work. They run in isolated sessions via the `opencode run` command.

**Available Sub-Agents:**
- **`coder`** (`.opencode/agent/coder.md`): Writes and modifies code based on task requirements

#### 3. Custom Commands
Custom commands are defined in `.opencode/command/` and act as the user interface to the orchestrator:
- **`/agent:start`**: Queues a new task (with optional retry/priority settings)
- **`/agent:run`**: Executes the next pending task
- **`/agent:run-parallel`**: Executes multiple pending tasks concurrently (NEW - Phase 2)
- **`/agent:status`**: Shows task queue status, reconciles completed tasks, detects failures, and triggers auto-retries
- **`/agent:retry`**: Manually retries a failed task (NEW - Phase 2)
- **`/agent:cancel`**: Cancels a running or pending task
- **`/agent:clean`**: Removes old task files based on filter criteria

## Workflow

### 1. Task Creation (`/agent:start <agent_name> <prompt> [options]`)

**Command File:** `.opencode/command/agent-start.md`

**What Happens:**
1. The command invokes the "Setup Assistant" role
2. Generates a unique task ID using timestamp: `task_<timestamp>`
3. Parses optional flags: `--max-retries N`, `--auto-retry`, `--priority N`
4. Creates a task definition file at `.gemini/agents/tasks/<Task_ID>.json`:
   ```json
   {
     "taskId": "task_1234567890",
     "status": "pending",
     "agent": "coder",
     "prompt": "User's task description",
     "planFile": ".gemini/agents/plans/task_1234567890_plan.md",
     "logFile": ".gemini/agents/logs/task_1234567890.log",
     "createdAt": "2025-12-01T00:00:00Z",
     "retryCount": 0,
     "maxRetries": 3,
     "autoRetry": false,
     "priority": 5,
     "parentTaskId": null
   }
   ```
5. Creates an empty plan file at `.gemini/agents/plans/<Task_ID>_plan.md` with the task prompt
6. Responds: "Task <Task_ID> created for <agent_name>."

**Key Points:**
- Tasks start in `pending` status
- Each task gets a unique ID, plan file, and log file path
- Optional retry and priority settings can be configured at creation
- Multiple tasks can be queued

### 2. Task Execution (`/agent:run`)

**Command File:** `.opencode/command/agent-run.md`

**What Happens:**
1. The command invokes the "Master Orchestrator" role
2. Scans `.gemini/agents/tasks/` for the oldest `pending` task (by file timestamp)
3. Updates the task status to `running` in the JSON file
4. Launches the specified sub-agent asynchronously in the background:
   ```bash
   opencode run "Your Task ID is $TASK_ID. Task: $PROMPT. Signal completion by creating .gemini/agents/tasks/$TASK_ID.done" --agent $AGENT_NAME >> .gemini/agents/logs/$TASK_ID.log 2>&1 &
   ```
5. Records the process PID in the task JSON
6. Responds: "Started task <Task_ID> (PID: <PID>)."

**Key Points:**
- Only one task is executed per `/agent:run` invocation
- Tasks run asynchronously in the background
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
   - Writes or modifies code (in current directory or `.gemini/agents/workspace/`)
   - Creates a sentinel file: `.gemini/agents/tasks/<Task_ID>.done`
   - Reports the absolute paths of created files (to the log)

**Key Points:**
- Sub-agents run in isolated sessions
- They respect project conventions when found
- Completion is signaled via a `.done` file (not by exit status)
- The workspace can be the current directory or a dedicated workspace

### 4. Parallel Task Execution (`/agent:run-parallel [max_concurrent]`)

**Command File:** `.opencode/command/agent-run-parallel.md` (NEW - Phase 2)

**What Happens:**
1. The command invokes the "Parallel Task Launcher" role
2. Counts currently running tasks
3. Calculates available slots: `max_concurrent - running_count`
4. Finds the oldest pending tasks (up to available slots)
5. Launches each task in the background (same as `/agent:run`)
6. Records PIDs for all launched tasks
7. Responds: "Started N task(s): task_123, task_456 (PIDs: 12345, 12346)"

**Key Points:**
- Default concurrency limit: 3 tasks
- Respects system resources by limiting parallel execution
- Each task runs independently in its own process
- Use `/agent:status` to monitor progress of all running tasks

### 5. Task Retry (`/agent:retry <task_id> [max_retries] [--auto]`)

**Command File:** `.opencode/command/agent-retry.md` (NEW - Phase 2)

**What Happens:**
1. The command invokes the "Task Retry Manager" role
2. Validates the task exists and is in `failed` state
3. Extracts original task info (agent, prompt, error)
4. Checks if retry limit has been reached
5. Creates a new task with:
   - Same agent and prompt as original
   - Incremented `retryCount`
   - Linked via `parentTaskId` to original task
   - Optional `autoRetry` flag for automatic future retries
   - Updated `retryHistory` with failure details
6. Creates a plan file documenting the retry attempt
7. Updates original task with `retriedBy` field
8. Responds: "Task task_XXX created as retry for task_YYY (attempt 2/3)"

**Key Points:**
- Only failed tasks can be retried
- Retry count is tracked and enforced (default max: 3)
- Auto-retry flag enables automatic retries on future failures
- Full audit trail maintained via retryHistory
- Original task context is preserved

### 6. Status Check and Reconciliation (`/agent:status`)

**Command File:** `.opencode/command/agent-status.md`

**What Happens:**
1. The command invokes the "Status Reporter and Auto-Retry Manager" role
2. **Reconciliation Phase:**
   - Finds all tasks with `"status": "running"`
   - Checks if a corresponding `.done` file exists → updates to `complete`
   - Checks if a corresponding `.error` file exists → updates to `failed` and captures error message
   - Checks if a corresponding `.cancelled` file exists → updates to `cancelled`
   - Checks if PID is still alive → if process died without sentinel file, marks as `failed`
3. **Auto-Retry Phase (NEW - Phase 2):**
   - For each newly failed task with `autoRetry: true`:
     - Checks if `retryCount < maxRetries`
     - Calculates exponential backoff delay (2^retryCount seconds)
     - If delay has elapsed, automatically creates retry task
     - Reports: "Auto-retrying task_XXX (attempt N/M)"
4. **Reporting Phase:**
   - Reads all task JSON files
   - Outputs a Markdown table with columns:
     - ID (with ↻ symbol for retry tasks)
     - Agent
     - Status (✓ complete, ✗ failed, ⏱ running, ⏸ pending, ⊗ cancelled, 🔄 auto-retry)
     - Prompt (truncated summary)
     - Retry (shows "N/M" if retryCount > 0)
     - Error/Info (error message or retry countdown)
5. **Summary Statistics:**
   - Total, running, pending, completed, failed counts
   - Number of failed tasks with auto-retry enabled

**Key Points:**
- Reconciliation happens on-demand, not automatically
- Multiple sentinel files support different completion states
- PID health checking detects crashed processes
- Auto-retry triggers automatically for eligible tasks
- Exponential backoff prevents thrashing (2s, 4s, 8s, 16s...)
- Old completed tasks remain in the system unless manually cleaned

## Task States

Tasks can be in one of five states:

1. **`pending`**: Task created but not yet started
2. **`running`**: Task is being executed by a sub-agent (process is active)
3. **`complete`**: Task finished successfully (reconciled via `.done` file)
4. **`failed`**: Task failed (process died, error occurred, or explicit failure via `.error` file)
5. **`cancelled`**: Task was cancelled by user via `/agent:cancel`

## Error Handling and Task Management (Phase 1)

### Enhanced Status Reconciliation

The `/agent:status` command now performs comprehensive health checks:

- **Process Health**: Checks if PIDs for running tasks are still alive using `ps -p $PID`
- **Error Detection**: Detects `.error` sentinel files created by failing agents
- **Cancellation Detection**: Recognizes `.cancelled` files from cancelled tasks
- **Automatic Failover**: Updates tasks to `failed` state when process dies unexpectedly

### Task Cancellation (`/agent:cancel <task_id>`)

**Command File:** `.opencode/command/agent-cancel.md`

Cancel running or pending tasks gracefully:

- **Pending Tasks**: Immediately cancelled, status updated to `cancelled`
- **Running Tasks**: Process terminated with SIGTERM, then SIGKILL if needed
- **Completed/Failed Tasks**: Cannot be cancelled (reports current status)

**Usage:**
```bash
/agent:cancel task_1234567890
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

**Location**: `.gemini/agents/tasks/<Task_ID>.error`

**Format**: JSON with error details
```json
{
  "error": "Brief error description",
  "details": "Full error message or stack trace",
  "timestamp": "2025-12-01T10:30:00Z"
}
```

The status command reads these files, updates the task JSON with the error message, and deletes the `.error` file during reconciliation.

### Task Cleanup (`/agent:clean [filter]`)

**Command File:** `.opencode/command/agent-clean.md`

Remove old task files to keep the workspace clean:

**Filters:**
- `completed` (default) - Remove completed tasks
- `failed` - Remove failed tasks
- `cancelled` - Remove cancelled tasks
- `all` - Remove all non-running/non-pending tasks
- `task_XXXXX` - Remove specific task by ID

**Usage:**
```bash
/agent:clean completed    # Remove completed tasks
/agent:clean failed       # Remove failed tasks
/agent:clean all          # Remove all finished tasks
/agent:clean task_123     # Remove specific task
```

**Safety:** 
- Never deletes `running` or `pending` tasks
- Asks for confirmation if more than 10 tasks match
- Removes JSON, plan, log, and sentinel files

### Enhanced Task JSON Schema

Tasks now include retry tracking, priority, and error tracking fields:

```json
{
  "taskId": "task_1234567890",
  "status": "failed",
  "agent": "coder",
  "prompt": "Create a web server",
  "planFile": ".gemini/agents/plans/task_1234567890_plan.md",
  "logFile": ".gemini/agents/logs/task_1234567890.log",
  "createdAt": "2025-12-01T10:00:00Z",
  "pid": "12345",
  "errorMessage": "Process terminated unexpectedly",
  "retryCount": 1,
  "maxRetries": 3,
  "autoRetry": true,
  "priority": 5,
  "parentTaskId": "task_1234567000",
  "retriedBy": "task_1234567999",
  "retriedAt": "2025-12-01T10:05:00Z",
  "retryHistory": [
    {
      "attempt": 1,
      "timestamp": "2025-12-01T10:00:00Z",
      "error": "Network timeout",
      "retriedFrom": "task_1234567000"
    }
  ]
}
```

## Implementation Details

### How Custom Commands Work
- Custom commands are markdown files in `.opencode/command/`
- They contain YAML frontmatter with metadata and a prompt for the orchestrator
- The `agent: build` field specifies they use the build agent (the main OpenCode agent)
- Arguments (`$1`, `$2`, etc.) are passed from the slash command invocation

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

## Usage Examples

### Example 1: Simple Task
```bash
/agent:start coder Write a Hello World function in Python
/agent:run
# ... wait for completion ...
/agent:status
```

### Example 2: Multiple Tasks
```bash
/agent:start coder Create a REST API server
/agent:start coder Write unit tests for the API
/agent:status    # Shows 2 pending tasks
/agent:run       # Starts first task
/agent:run       # Starts second task
/agent:status    # Shows progress
```

### Example 3: Cancel and Retry
```bash
/agent:start coder Generate a large dataset
/agent:run
# Oops, wrong parameters!
/agent:status    # Get the task ID
/agent:cancel task_1234567890
/agent:start coder Generate a large dataset with correct parameters
/agent:run
```

### Example 4: Cleanup
```bash
/agent:status    # Check completed tasks
/agent:clean completed    # Remove all completed tasks
/agent:clean failed       # Remove failed tasks
/agent:clean all          # Remove all finished tasks
```

### Example 5: Parallel Execution (Phase 2)
```bash
# Queue multiple tasks
/agent:start coder Create user authentication module
/agent:start coder Write API documentation
/agent:start coder Implement logging system
/agent:start coder Add unit tests
/agent:start coder Create integration tests

# Check queue status
/agent:status
# | ID         | Agent | Status | Prompt                    |
# | task_12345 | coder | ⏸      | Create user auth...       |
# | task_12346 | coder | ⏸      | Write API docs...         |
# | task_12347 | coder | ⏸      | Implement logging...      |
# | task_12348 | coder | ⏸      | Add unit tests...         |
# | task_12349 | coder | ⏸      | Create integration...     |

# Launch 3 tasks in parallel (default concurrency)
/agent:run-parallel
# Started 3 task(s): task_12345, task_12346, task_12347 (PIDs: 98765, 98766, 98767)
# Running: 3/3 tasks

# Check status - 3 running concurrently
/agent:status
# | ID         | Agent | Status | Prompt                    |
# | task_12345 | coder | ⏱      | Create user auth...       |
# | task_12346 | coder | ⏱      | Write API docs...         |
# | task_12347 | coder | ⏱      | Implement logging...      |
# | task_12348 | coder | ⏸      | Add unit tests...         |
# | task_12349 | coder | ⏸      | Create integration...     |

# After some tasks complete, launch remaining
/agent:run-parallel
# Started 2 task(s): task_12348, task_12349 (PIDs: 98768, 98769)
# Running: 3/3 tasks

# Launch with higher concurrency
/agent:run-parallel 5
# Started 5 task(s): ... (PIDs: ...)
```

### Example 6: Manual Retry (Phase 2)
```bash
# Task fails
/agent:status
# | ID         | Agent | Status | Prompt                | Error              |
# | task_12345 | coder | ✗      | Deploy to prod...     | Network timeout    |

# Retry the failed task
/agent:retry task_12345
# Task task_12346 created as retry for task_12345 (attempt 1/3)
# Use /agent:run or /agent:run-parallel to execute the retry

# Run the retry
/agent:run
# Started task task_12346 (PID: 98770)

# Check status - shows retry link
/agent:status
# | ID         | Agent | Status | Prompt                | Retry |
# | task_12345 | coder | ✗      | Deploy to prod...     |       |
# | ↻ task_12346 | coder | ⏱      | Deploy to prod...     | 1/3   |
```

### Example 7: Auto-Retry (Phase 2)
```bash
# Create task with auto-retry enabled
/agent:start coder "Deploy microservice to production" --max-retries 5 --auto-retry
# Task task_12345 created for coder.
# Max retries: 5
# Auto-retry: enabled

# Run the task
/agent:run
# Started task task_12345 (PID: 98765)

# Task fails, check status
/agent:status
# Auto-retrying task_12345 (attempt 2/5)
# | ID           | Agent | Status | Prompt                | Retry | Error/Info        |
# | task_12345   | coder | ✗      | Deploy microser...    | 1/5   | Connection failed |
# | ↻ task_12346 | coder | ⏸      | Deploy microser...    | 2/5   | auto-retry        |

# Wait for backoff delay (2^1 = 2 seconds), then status again
/agent:status
# Task task_12346 automatically queued for execution

# Run it
/agent:run
# Started task task_12346 (PID: 98766)

# Fails again - longer backoff
/agent:status
# | ID           | Agent | Status | Prompt                | Retry | Error/Info        |
# | task_12345   | coder | ✗      | Deploy microser...    | 1/5   | Connection failed |
# | task_12346   | coder | ✗      | Deploy microser...    | 2/5   | Connection failed |
# | ↻ task_12347 | coder | 🔄     | Deploy microser...    | 3/5   | retry in 4s       |

# After 4 seconds, auto-retry triggers
/agent:status
# | ↻ task_12347 | coder | ⏸      | Deploy microser...    | 3/5   | auto-retry        |

# Eventually succeeds
/agent:run
/agent:status
# | ID           | Agent | Status | Prompt                | Retry |
# | ↻ task_12347 | coder | ✓      | Deploy microser...    | 3/5   |
```

### Example 8: Combining Parallel Execution and Auto-Retry (Phase 2)
```bash
# Queue multiple tasks with auto-retry
/agent:start coder "Task 1" --auto-retry
/agent:start coder "Task 2" --auto-retry
/agent:start coder "Task 3" --auto-retry
/agent:start coder "Task 4" --auto-retry

# Launch all in parallel
/agent:run-parallel 4
# Started 4 task(s): task_12345, task_12346, task_12347, task_12348

# Some tasks fail, auto-retry kicks in
/agent:status
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
/agent:run-parallel
# Started 2 task(s): task_12349, task_12350
```

## Extending the Framework

### Adding a New Sub-Agent
1. Create a new file in `.opencode/agent/<agent_name>.md`
2. Define the agent's role, tools, and protocol
3. Ensure it creates a `.done` file upon completion
4. Use it via `/agent:start <agent_name> <prompt>`

### Adding a New Command
1. Create a new file in `.opencode/command/<command_name>.md`
2. Define the command's description and behavior in the prompt
3. Invoke it via `/<command_name>`

## Limitations and Considerations

### Resolved (Phase 1)
- ✅ **Task cancellation**: Now available via `/agent:cancel` command
- ✅ **Failure handling**: Failed tasks are now detected via PID health checks and `.error` files
- ✅ **Task cleanup**: Now available via `/agent:clean` command

### Resolved (Phase 2)
- ✅ **Parallel execution**: Now available via `/agent:run-parallel` command with configurable concurrency
- ✅ **Retry mechanism**: Now available via `/agent:retry` command with auto-retry and exponential backoff

### Current Limitations
- **No automatic cleanup**: Completed tasks remain until manually removed via `/agent:clean`
- **No task prioritization**: Tasks execute in FIFO order (oldest first) - priority field exists but not yet used
- **Manual reconciliation**: Status updates require explicit `/agent:status` call
- **No timeout handling**: Long-running tasks are not automatically terminated
