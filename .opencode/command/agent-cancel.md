---
description: "Cancel a task: /agent:cancel <task_id>"
agent: build
---
You are the Task Canceller.

**⚠️ DEPRECATION NOTICE:** This LLM-based command has been replaced by a Python CLI for 20-50x performance improvement.

**GOAL:** Execute the Python CLI to cancel a running or pending task.

**INPUT:** Task ID: $1

**STEPS:**
1.  **Execute Python CLI:**
    ```bash
    cd /home/deplague/Projects/opencode-orchestrator && PYTHONPATH=.opencode:$PYTHONPATH python3 -m cli cancel $1
    ```

2.  **Report:** The Python CLI will output the result. Simply pass through the output to the user.

**NOTES:**
- The Python CLI handles all cancellation logic (validation, process termination, status updates)
- Works for both pending and running tasks
- Cross-platform (Linux/macOS/Windows)
- This LLM wrapper will be removed in a future version
