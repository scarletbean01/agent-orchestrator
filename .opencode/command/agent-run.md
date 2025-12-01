---
description: "Process the next pending task."
agent: build
---
You are the Master Orchestrator.

**GOAL:** Find the oldest "pending" task and execute it.

**STEPS:**
1.  **Scan:** List files in `.gemini/agents/tasks/`. Read them to find the oldest with `"status": "pending"`.
2.  **Lock:** If found, update its status to `"running"` AND set `"startedAt": "<ISO_TIMESTAMP>"` using proper JSON update.
3.  **Execute:** Construct and run the following command in the background:
    ```bash
    # Extract timeout value from task JSON (may be null)
    TIMEOUT=$(jq -r '.timeout // "null"' .gemini/agents/tasks/$TASK_ID.json)
    
    # Run using the helper script
    # Note: Using nohup or just backgrounding to ensure it persists
    .opencode/scripts/run-with-timeout.sh "$TASK_ID" "$TIMEOUT" "$AGENT_NAME" "$PROMPT" >> ".gemini/agents/logs/$TASK_ID.log" 2>&1 &
    
    # Capture the PID of the background process
    PID=$!
    ```
4.  **Record:** Update the JSON file with the new PID and ensure startedAt is set.
5.  **Report:** 
    - "Started task $TASK_ID (PID: <PID>)."
    - If timeout is set: "Timeout: <timeout>s (<human_readable>)"

If no pending tasks are found, say "No pending tasks."

**NOTES:**
- The helper script handles GNU timeout logic and sentinel file creation
- Exit code 124 indicates timeout occurred
- The startedAt timestamp is used for elapsed time display
