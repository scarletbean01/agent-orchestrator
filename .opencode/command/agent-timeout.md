---
description: "Manage task timeouts: /agent:timeout <task_id> | list | extend <task_id> <seconds>"
agent: build
---
You are the Timeout Manager.

**⚠️ DEPRECATION NOTICE:** This LLM-based command has been replaced by a Python CLI for 20-50x performance improvement.

**GOAL:** Execute the Python CLI to manage task timeouts.

**INPUTS:**
- Command: $1 (task_id, "list", or "extend")
- Additional Args: $2, $3 (for extend command)

**STEPS:**
1.  **Execute Python CLI:**
    ```bash
    cd /home/deplague/Projects/opencode-orchestrator && PYTHONPATH=.opencode:$PYTHONPATH python3 -m cli timeout $1 $2 $3
    ```

2.  **Report:** The Python CLI will output the result. Simply pass through the output to the user.

**NOTES:**
- The Python CLI handles all timeout logic (immediate timeout, listing, extending)
- Subcommands: `list`, `extend <task_id> <seconds>`, or `<task_id>` to timeout immediately
- This LLM wrapper will be removed in a future version

**GOAL:** Provide manual control over task timeouts.

**INPUTS:**
- Command: $1 (task_id to timeout immediately, "list" to show timeout status, "extend")
- Additional Args: $2 (task_id for extend), $3 (seconds for extend)

**COMMANDS:**

### 1. Immediate Timeout: `/agent:timeout <task_id>`
**STEPS:**
1. Read the task JSON file for <task_id>
2. Validate task exists and status is "running"
3. If task has no PID, report error: "Task has no PID recorded"
4. Terminate the process (GNU timeout will handle graceful shutdown):
   - Send SIGTERM to PID: `kill -TERM $PID`
   - Wait 3 seconds: `sleep 3`
   - Check if still alive: `ps -p $PID > /dev/null 2>&1`
   - If still alive, send SIGKILL: `kill -9 $PID`
5. Create `.timeout` sentinel file:
   ```bash
   echo "{\"timeout\": \"manual\", \"timestamp\": \"$(date -Iseconds)\"}" > .gemini/agents/tasks/$TASK_ID.timeout
   ```
6. Report: "Task <task_id> terminated (will be marked as timed out on next status check)"

**NOTE:** The actual status update happens during the next `/agent:status` run when it detects the `.timeout` file.

### 2. List Timeouts: `/agent:timeout list`
**STEPS:**
1. Read all task JSON files in `.gemini/agents/tasks/`
2. Filter for tasks with `"timeout"` field set (not null)
3. For running tasks, calculate elapsed time from `startedAt`
4. Output a Markdown table with columns:
   - ID
   - Status
   - Timeout Limit (human readable)
   - Elapsed (if running, human readable)
   - Remaining (if running, human readable)
   - Status Indicator (✓ complete, ⏱ running, ⚠ warning, ⏱⚠ critical, ✗ timed out)
5. Summary:
   - Total tasks with timeouts: X
   - Running with timeouts: Y (Z in warning zone)
   - Timed out: A

### 3. Extend Timeout: `/agent:timeout extend <task_id> <seconds>`

**WARNING:** Extending timeout for a running task with GNU timeout is complex because:
- The timeout process is already running with a specific duration
- Cannot dynamically extend a running timeout process
- Would require killing and restarting the task

**RECOMMENDED APPROACH:**
1. Inform user that extending timeout requires task restart
2. Provide instructions:
   ```
   To extend timeout for a running task:
   1. Cancel the task: /agent:cancel <task_id>
   2. Create new task with extended timeout: /agent:start <agent> "<prompt>" --timeout <new_timeout>
   3. Run the new task: /agent:run
   ```

**ALTERNATIVE (simpler but less useful):**
1. Read the task JSON file for <task_id>
2. Validate task exists
3. Update the `timeout` field in JSON (for documentation purposes only)
4. Report: "Timeout value updated in task metadata, but running process timeout cannot be extended. Consider canceling and restarting with new timeout."

**ERROR HANDLING:**
- If task_id doesn't exist: "Task <task_id> not found"
- If invalid seconds value: "Invalid seconds value: <value>"
