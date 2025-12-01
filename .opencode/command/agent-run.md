---
description: "Process the next pending task."
agent: build
---
You are the Master Orchestrator.

**GOAL:** Find the oldest "pending" task and execute it.

**STEPS:**
1.  **Scan:** List files in `.gemini/agents/tasks/`. Read them to find the oldest with `"status": "pending"`.
2.  **Lock:** If found, update its status to `"running"` AND set `"startedAt": "<ISO_TIMESTAMP>"` using proper JSON update.
3.  **Execute:** Detect the execution environment to choose the correct script.

    **Environment Detection:**
    - First, test if `jq` is available: `command -v jq > /dev/null 2>&1`
    - Check your `<env>` context for the "Platform" field.

    **If `jq` is available OR Platform is "linux" or "darwin" (macOS):**
    - Use the Bash script (Unix-style execution):
    ```bash
    # Extract timeout value from task JSON
    TIMEOUT=$(jq -r '.timeout // "null"' .gemini/agents/tasks/$TASK_ID.json)
    
    # Run the Bash helper script in background
    .opencode/scripts/run-with-timeout.sh "$TASK_ID" "$TIMEOUT" "$AGENT_NAME" "$PROMPT" >> ".gemini/agents/logs/$TASK_ID.log" 2>&1 &
    
    # Capture the PID of the background process
    PID=$!
    ```

    **If `jq` is NOT available AND Platform is "windows":**
    - Use the hybrid approach for Git Bash on Windows:
    ```bash
    # Use PowerShell to read JSON, but invoke from Bash
    TIMEOUT=$(powershell -Command "(Get-Content .gemini/agents/tasks/$TASK_ID.json | ConvertFrom-Json).timeout")
    if [ -z "$TIMEOUT" ] || [ "$TIMEOUT" = "" ]; then TIMEOUT="null"; fi
    
    # Start PowerShell script in background and capture its PID
    powershell -ExecutionPolicy Bypass -Command "Start-Process -NoNewWindow -FilePath 'powershell' -ArgumentList '-ExecutionPolicy','Bypass','-File','.opencode/scripts/run-with-timeout.ps1','-TaskId','$TASK_ID','-Timeout','$TIMEOUT','-AgentName','$AGENT_NAME','-Prompt', ''''$PROMPT'''' -RedirectStandardOutput '.gemini/agents/logs/$TASK_ID.log' -RedirectStandardError '.gemini/agents/logs/$TASK_ID.log' -PassThru | Select-Object -ExpandProperty Id | Out-File -FilePath '.gemini/agents/tasks/$TASK_ID.pid' -NoNewline"
    
    # Read the PID from the file
    PID=$(cat .gemini/agents/tasks/$TASK_ID.pid)
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
