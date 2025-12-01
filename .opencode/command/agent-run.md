---
description: "Process the next pending task."
agent: build
---
You are the Master Orchestrator.

**⚠️ DEPRECATION NOTICE:** This LLM-based command has been replaced by a Python CLI for 20-50x performance improvement.

**GOAL:** Execute the Python CLI to run the next pending task.

**STEPS:**
1.  **Execute Python CLI:**
    ```bash
    cd /home/deplague/Projects/opencode-orchestrator && PYTHONPATH=.opencode:$PYTHONPATH python3 -m cli run
    ```

2.  **Report:** The Python CLI will output the result. Simply pass through the output to the user.

**NOTES:**
- The Python CLI handles all task execution logic (scanning, locking, launching)
- For parallel execution, use `/agent:run-parallel [N]` instead
- This LLM wrapper will be removed in a future version
