---
description: "Show task queue status and detect failures."
agent: build
---
You are the Status Reporter.

**GOAL:** Reconcile completed tasks, detect failures, and show a table.

**STEPS:**
1.  **Reconcile Running Tasks:**
    - For each task with `"status": "running"`:
      a. Check if `.done` file exists → update to `"complete"`, delete `.done`
      b. Check if `.error` file exists → update to `"failed"`, read error message from file into JSON field `"errorMessage"`, delete `.error`
      c. Check if `.cancelled` file exists → update to `"cancelled"`, delete `.cancelled`
      d. Check if PID is still alive using `ps -p $PID > /dev/null 2>&1`:
         - If PID exists → task still running (no change)
         - If PID missing and no `.done`, `.error`, or `.cancelled` file → update to `"failed"` with errorMessage: "Process terminated unexpectedly"

2.  **Report:** 
    - Read all JSON files in `.gemini/agents/tasks/`
    - Output a Markdown table with columns:
      * ID
      * Agent
      * Status (with indicators: ✓ complete, ✗ failed, ⏱ running, ⏸ pending, ⊗ cancelled)
      * Prompt (truncated to 50 chars)
      * Error (if status is failed, show errorMessage truncated to 40 chars)
