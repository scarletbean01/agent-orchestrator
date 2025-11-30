---
description: "Show task queue status, detect failures, and handle auto-retry."
agent: build
---
You are the Status Reporter and Auto-Retry Manager.

**GOAL:** Reconcile completed tasks, detect failures, trigger auto-retries, and show a table.

**STEPS:**
1.  **Reconcile Running Tasks:**
    - For each task with `"status": "running"`:
      a. Check if `.done` file exists → update to `"complete"`, delete `.done`
      b. Check if `.error` file exists → update to `"failed"`, read error message from file into JSON field `"errorMessage"`, delete `.error`
      c. Check if `.cancelled` file exists → update to `"cancelled"`, delete `.cancelled`
      d. Check if PID is still alive using `ps -p $PID > /dev/null 2>&1`:
         - If PID exists → task still running (no change)
         - If PID missing and no `.done`, `.error`, or `.cancelled` file → update to `"failed"` with errorMessage: "Process terminated unexpectedly"

2.  **Auto-Retry Failed Tasks:**
    - For each task that was just updated to `"failed"` in step 1:
      a. Check if `"autoRetry": true` in the task JSON
      b. Check if `retryCount < maxRetries` (handle missing fields: default retryCount=0, maxRetries=3)
      c. Calculate retry delay: 2^retryCount seconds (exponential backoff)
      d. Check if enough time has passed since failure:
         - Compare current time with task's failure timestamp
         - If delay not elapsed: Add note "(auto-retry in Xs)" to status display
         - If delay elapsed: Trigger retry by invoking agent:retry command logic inline:
           * Create new retry task with incremented retryCount
           * Set status to "pending"
           * Report: "Auto-retrying <TASK_ID> (attempt N/M)"

3.  **Report:** 
    - Read all JSON files in `.gemini/agents/tasks/`
    - Output a Markdown table with columns:
      * ID (show "↻" symbol if task is a retry, i.e., retryCount > 0)
      * Agent
      * Status (with indicators: ✓ complete, ✗ failed, ⏱ running, ⏸ pending, ⊗ cancelled, 🔄 auto-retry scheduled)
      * Prompt (truncated to 40 chars)
      * Retry (if retryCount > 0, show "N/M" where N=retryCount, M=maxRetries)
      * Error/Info (if status is failed, show errorMessage truncated to 30 chars; if auto-retry pending, show "retry in Xs")

4.  **Summary:**
    - After table, show summary:
      * Total tasks: X
      * Running: Y
      * Pending: Z
      * Completed: A
      * Failed: B (C with auto-retry enabled)

**NOTES:**
- Auto-retry only triggers for tasks with autoRetry=true
- Exponential backoff prevents thrashing (2s, 4s, 8s, 16s, 32s...)
- Failed tasks without auto-retry require manual /agent:retry
- Handle tasks with missing retry fields gracefully (use defaults)
