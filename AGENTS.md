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
│   ├── agent-status.md
│   ├── agent-cancel.md    # NEW: Cancel tasks
│   └── agent-clean.md     # NEW: Cleanup old tasks
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
- **`/agent:start`**: Queues a new task
- **`/agent:run`**: Executes the next pending task
- **`/agent:status`**: Shows task queue status, reconciles completed tasks, and detects failures
- **`/agent:cancel`**: Cancels a running or pending task
- **`/agent:clean`**: Removes old task files based on filter criteria

## Workflow

### 1. Task Creation (`/agent:start <agent_name> <prompt>`)

**Command File:** `.opencode/command/agent-start.md`

**What Happens:**
1. The command invokes the "Setup Assistant" role
2. Generates a unique task ID using timestamp: `task_<timestamp>`
3. Creates a task definition file at `.gemini/agents/tasks/<Task_ID>.json`:
   ```json
   {
     "taskId": "task_1234567890",
     "status": "pending",
     "agent": "coder",
     "prompt": "User's task description",
     "planFile": ".gemini/agents/plans/task_1234567890_plan.md",
     "logFile": ".gemini/agents/logs/task_1234567890.log",
     "createdAt": "2025-12-01T00:00:00Z"
   }
   ```
4. Creates an empty plan file at `.gemini/agents/plans/<Task_ID>_plan.md` with the task prompt
5. Responds: "Task <Task_ID> created for <agent_name>."

**Key Points:**
- Tasks start in `pending` status
- Each task gets a unique ID, plan file, and log file path
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

### 4. Status Check and Reconciliation (`/agent:status`)

**Command File:** `.opencode/command/agent-status.md`

**What Happens:**
1. The command invokes the "Status Reporter" role
2. **Reconciliation Phase:**
   - Finds all tasks with `"status": "running"`
   - Checks if a corresponding `.done` file exists → updates to `complete`
   - Checks if a corresponding `.error` file exists → updates to `failed` and captures error message
   - Checks if a corresponding `.cancelled` file exists → updates to `cancelled`
   - Checks if PID is still alive → if process died without sentinel file, marks as `failed`
3. **Reporting Phase:**
   - Reads all task JSON files
   - Outputs a Markdown table with columns:
     - ID
     - Agent
     - Status (✓ complete, ✗ failed, ⏱ running, ⏸ pending, ⊗ cancelled)
     - Prompt (truncated summary)
     - Error (for failed tasks, shows error message)

**Key Points:**
- Reconciliation happens on-demand, not automatically
- Multiple sentinel files support different completion states
- PID health checking detects crashed processes
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

Tasks now include optional error tracking fields:

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
  "errorMessage": "Process terminated unexpectedly"
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

### Current Limitations
- **No automatic cleanup**: Completed tasks remain until manually removed via `/agent:clean`
- **No task prioritization**: Tasks execute in FIFO order (oldest first)
- **No parallel execution**: One task executes at a time (though they run async)
- **Manual reconciliation**: Status updates require explicit `/agent:status` call
- **No timeout handling**: Long-running tasks are not automatically terminated
- **No retry mechanism**: Failed tasks must be manually recreated
