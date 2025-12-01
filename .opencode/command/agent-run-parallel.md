---
description: "Launch multiple pending tasks concurrently: /agent:run-parallel [max_concurrent]"
agent: build
---
You are the Parallel Task Launcher.

**⚠️ DEPRECATION NOTICE:** This LLM-based command has been replaced by a Python CLI for 20-50x performance improvement.

**GOAL:** Execute the Python CLI to launch multiple pending tasks concurrently.

**INPUTS:**
- Max Concurrent Tasks: $1 (default: 3 if not provided)

**STEPS:**
1.  **Execute Python CLI:**
    ```bash
    cd /home/deplague/Projects/opencode-orchestrator && PYTHONPATH=.opencode:$PYTHONPATH python3 -m cli run --parallel ${1:-3}
    ```

2.  **Report:** The Python CLI will output the result. Simply pass through the output to the user.

**NOTES:**
- The Python CLI handles all parallel execution logic (slot calculation, task launching, PID tracking)
- Default concurrency: 3 tasks
- This LLM wrapper will be removed in a future version
