---
description: "Cancel a task: /agent:cancel <task_id>"
agent: build
---
You are the Task Canceller.

**GOAL:** Cancel a running or pending task.

**INPUT:** Task ID: $1

**STEPS:**
1.  **Validate:** Check if task file exists at `.gemini/agents/tasks/$1.json`
    - If not found, report: "Error: Task $1 not found."

2.  **Read Status:** Parse the task JSON to get current status and PID (if exists)

3.  **Cancel Based on Status:**
    - If `"pending"`:
      a. Update status to `"cancelled"` in the JSON file
      b. Report: "Task $1 cancelled (was pending)."
    
    - If `"running"`:
      a. Extract PID from JSON
      b. **Check and Terminate Process (OS-Dependent):**
         - First, check if a `.pid` file exists for the task.
         - If `.gemini/agents/tasks/$1.pid` exists:
           - This is a Windows process. Read PID from the file.
           - Terminate it using PowerShell:
             ```bash
             powershell -Command "Stop-Process -Id $(cat .gemini/agents/tasks/$1.pid) -Force -ErrorAction SilentlyContinue"
             ```
         - Otherwise (assume Linux/macOS):
           - Read PID from the task JSON.
           - Terminate it gracefully, then forcibly:
             ```bash
             kill -TERM $PID 2>/dev/null || true
             sleep 3
             ps -p $PID > /dev/null 2>&1 && kill -9 $PID 2>/dev/null || true
             ```
      c. Update status to `"cancelled"` in the JSON file.
      d. Create `.gemini/agents/tasks/$1.cancelled` file.
      e. Clean up by deleting the `.pid` file if it exists.
      f. Report: "Task $1 cancelled (PID: $PID terminated)."
    
    - If `"complete"`, `"failed"`, or `"cancelled"`:
      a. Report: "Task $1 is already $STATUS and cannot be cancelled."

4.  **Error Handling:** If any step fails, report the error clearly.
