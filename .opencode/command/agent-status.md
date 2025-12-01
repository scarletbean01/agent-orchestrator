---
description: "Show task queue status, detect failures/timeouts, and handle auto-retry."
agent: build
---
You are the Status Reporter, Timeout Manager, and Auto-Retry Manager.

**GOAL:** Reconcile completed tasks, detect failures and timeouts, trigger auto-retries, and show a table.

**STEPS:**
1.  **Reconcile Running Tasks:**
    - For each task with `"status": "running"`:
      a. Check if `.done` file exists → update to `"complete"`, delete `.done`, delete `.exitcode`
      
      b. Check if `.error` file exists → update to `"failed"`, read error message from file into JSON field `"errorMessage"`, delete `.error`, delete `.exitcode`
      
      c. Check if `.cancelled` file exists → update to `"cancelled"`, delete `.cancelled`, delete `.exitcode`
      
      d. **Check for timeout (via GNU timeout sentinel):**
         - Check if `.timeout` file exists (created by run-with-timeout.sh)
         - If exists:
           * Read timeout info from `.timeout` file
           * Update status to `"failed"`
           * Set `"errorMessage": "Task timed out after <timeout> seconds"`
           * Set `"timedOutAt": "<ISO_TIMESTAMP>"`
           * Delete `.timeout` and `.exitcode` files
           * Continue to next task
      
      e. Check if PID is still alive using `ps -p $PID > /dev/null 2>&1`:
         - If PID exists → task still running (no change)
         - If PID missing:
           * Check if `.exitcode` file exists
           * If exitcode file exists and contains 124 → should have .timeout file (handle as timeout)
           * If exitcode file exists and contains non-zero value → update to `"failed"` with errorMessage: "Process exited with code <N>"
           * If no .done, .error, .cancelled, or .timeout file → update to `"failed"` with errorMessage: "Process terminated unexpectedly"
           * Delete `.exitcode` file

2.  **Auto-Retry Failed Tasks:**
    - For each task that was just updated to `"failed"` in step 1:
      a. Check if `"autoRetry": true` in the task JSON
      b. Check if `retryCount < maxRetries` (handle missing fields: default retryCount=0, maxRetries=3)
      c. Calculate retry delay: 2^retryCount seconds (exponential backoff)
      d. Check if enough time has passed since failure:
         - Compare current time with task's failure timestamp (timedOutAt or last update)
         - If delay not elapsed: Add note "(auto-retry in Xs)" to status display
         - If delay elapsed: Trigger retry by invoking agent:retry command logic inline:
           * Create new retry task with incremented retryCount
           * Inherit timeout setting from parent task
           * Set status to "pending"
           * Report: "Auto-retrying <TASK_ID> (attempt N/M)"

3.  **Report:** 
    - Read all JSON files in `.gemini/agents/tasks/`
    - Output a Markdown table with columns:
      * ID (show "↻" symbol if task is a retry, i.e., retryCount > 0)
      * Agent
      * Status (with indicators: ✓ complete, ✗ failed, ⏱ running, ⏸ pending, ⊗ cancelled, 🔄 auto-retry scheduled, ⏱⚠ timeout warning)
      * Prompt (truncated to 40 chars)
      * Time (for running tasks: show "elapsed / timeout" or just "elapsed" if no timeout; for timed out tasks: "⏱ timeout")
      * Retry (if retryCount > 0, show "N/M" where N=retryCount, M=maxRetries)
      * Error/Info (if status is failed, show errorMessage truncated to 30 chars; if auto-retry pending, show "retry in Xs")
    
    **Time Column Examples:**
    - Running with timeout: "5m 30s / 1h" (elapsed / limit)
    - Running without timeout: "5m 30s" (elapsed only)
    - Running near timeout (within timeoutWarning): "⚠ 2m left"
    - Timed out: "⏱ timeout"
    - Not started/completed: "-"

4.  **Summary:**
    - After table, show summary:
      * Total tasks: X
      * Running: Y (Z with timeouts, A nearing timeout)
      * Pending: Z
      * Completed: A
      * Failed: B (C with auto-retry enabled, D timed out)

**NOTES:**
- GNU timeout automatically handles SIGTERM → SIGKILL for timed-out processes
- Exit code 124 from timeout command indicates timeout occurred
- No manual timeout checking or process killing needed in status command
- Timed out tasks can trigger auto-retry if enabled
