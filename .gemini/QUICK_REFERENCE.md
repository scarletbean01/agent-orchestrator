# OpenCode Agent Orchestrator - Quick Reference

## Available Commands

### Task Management
- `/agent:start <agent> <prompt>` - Queue a new task
- `/agent:run` - Execute the next pending task
- `/agent:status` - Show all tasks and reconcile completion/failures
- `/agent:cancel <task_id>` - Cancel a pending or running task
- `/agent:clean [filter]` - Remove old task files

### Cleanup Filters
- `completed` - Remove completed tasks only (default)
- `failed` - Remove failed tasks only
- `cancelled` - Remove cancelled tasks only
- `all` - Remove all non-running/non-pending tasks
- `task_XXXXX` - Remove a specific task by ID

## Task States

| State | Icon | Description |
|-------|------|-------------|
| pending | ⏸ | Task queued, not started |
| running | ⏱ | Task currently executing |
| complete | ✓ | Task finished successfully |
| failed | ✗ | Task crashed or reported error |
| cancelled | ⊗ | Task cancelled by user |

## Common Workflows

### Basic Task Execution
```bash
/agent:start coder Write a Python script
/agent:run
/agent:status
```

### Cancel a Task
```bash
/agent:status              # Get task ID
/agent:cancel task_123456  # Cancel it
```

### Cleanup Old Tasks
```bash
/agent:clean completed     # Remove completed tasks
/agent:clean failed        # Remove failed tasks
/agent:clean all           # Remove all finished tasks
```

### Handle Failures
```bash
/agent:status              # Check for failed tasks (shows error message)
# Review log file: .gemini/agents/logs/task_XXXXX.log
/agent:clean failed        # Clean up after investigation
```

## File Locations

- **Task Definitions**: `.gemini/agents/tasks/<task_id>.json`
- **Task Plans**: `.gemini/agents/plans/<task_id>_plan.md`
- **Task Logs**: `.gemini/agents/logs/<task_id>.log`
- **Output Code**: `.gemini/agents/workspace/` or project root

## Sentinel Files

- `.done` - Task completed successfully
- `.error` - Task failed (contains error JSON)
- `.cancelled` - Task was cancelled

## Tips

1. Always run `/agent:status` after waiting for tasks to complete
2. Check log files for detailed output: `.gemini/agents/logs/task_XXXXX.log`
3. Use `/agent:clean` regularly to keep the workspace tidy
4. Cancel long-running tasks safely with `/agent:cancel`
5. Failed tasks show error messages in the status table

## Error Handling

When a task fails:
1. Run `/agent:status` to see the error message
2. Check the log file for full details
3. Fix the issue in your prompt or code
4. Clean up the failed task: `/agent:clean failed`
5. Retry with a corrected prompt

