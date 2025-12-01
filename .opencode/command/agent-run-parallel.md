---
description: "Launch multiple pending tasks concurrently: /agent:run-parallel [max_concurrent]"
agent: build
---
You are the Parallel Task Launcher.

**GOAL:** Launch multiple pending tasks concurrently, respecting the concurrency limit.

**INPUTS:**
- Max Concurrent Tasks: $1 (default: 3 if not provided)

**STEPS:**
1.  **Count Running Tasks:**
    - List all JSON files in `.gemini/agents/tasks/`
    - Count tasks with `"status": "running"`
    - Store count as `RUNNING_COUNT`

2.  **Calculate Available Slots:**
    - MAX_CONCURRENT = $1 (or 3 if $1 is empty)
    - AVAILABLE_SLOTS = MAX_CONCURRENT - RUNNING_COUNT
    - If AVAILABLE_SLOTS <= 0, report "Already running $RUNNING_COUNT tasks (max: $MAX_CONCURRENT). No slots available." and exit.

3.  **Find Pending Tasks:**
    - List JSON files in `.gemini/agents/tasks/`
    - Read each file to find tasks with `"status": "pending"`
    - Sort by file modification time (oldest first)
    - Take the first AVAILABLE_SLOTS tasks

4.  **Launch Each Task:**
    - For each pending task found (up to AVAILABLE_SLOTS):
      a. Update its status to `"running"` AND set `"startedAt": "<ISO_TIMESTAMP>"` in the JSON file
      b. Extract TASK_ID, PROMPT, AGENT_NAME from JSON
      c. Launch the task in background:
         ```bash
         TIMEOUT=$(jq -r '.timeout // "null"' .gemini/agents/tasks/$TASK_ID.json)
         
         .opencode/scripts/run-with-timeout.sh "$TASK_ID" "$TIMEOUT" "$AGENT_NAME" "$PROMPT" >> ".gemini/agents/logs/$TASK_ID.log" 2>&1 &
         
         PID=$!
         ```
      d. Update the JSON file with the PID
      e. Add TASK_ID to a list of started tasks

5.  **Report:**
    - If no pending tasks found: "No pending tasks to launch."
    - If tasks were launched: "Started N task(s): task_123, task_456, task_789 (PIDs: 12345, 12346, 12347)"
    - Include current utilization: "Running: X/Y tasks"
    - For tasks with timeouts, list: "Timeouts: task_123 (5m), task_456 (1h)"

**NOTES:**
- The helper script handles GNU timeout logic and sentinel file creation
- Exit codes are captured for timeout detection (124 = timeout)
- Always record startedAt timestamp for elapsed time tracking
